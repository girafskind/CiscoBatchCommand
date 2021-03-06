#!/usr/bin/python
# Cisco IOS bulk command sender
# Takes CSV file with IPs, logs into device and gathers MAC address table, without the ones marked with CPU
# 15th of june 2020
# Bo Vittus Mortensen
# Version 1.0

import logging
from netmiko import ConnectHandler
from netmiko.ssh_exception import AuthenticationException, NetMikoTimeoutException
from datetime import datetime
from getpass import getpass

logger = logging.getLogger('netscript')
hdlr = logging.FileHandler('status.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


def main():
    logger.debug('Starting to collect MAC addreses')
    start_time = datetime.now()

    with open('devices.csv', 'r') as devices:
        for line in devices:
            runcommand(line)

    print("\nOperation took: {}".format(datetime.now() - start_time))
    input("\nPress Enter to continue...")


def runcommand(devicestring):
    device_handler = {'username': my_user, 'password': my_pass, 'ip': devicestring.split(";")[0],
                      'device_type': "cisco_ios"}
    configset = "show mac address-table | e CPU"

    try:
        switch_conn = ConnectHandler(**device_handler)
        logger.debug('Handler connected to ' + device_handler['ip'])
        print("Handler connected")
        hostname = switch_conn.find_prompt().replace("#", "")
        mac_result = switch_conn.send_command(configset)

        output = open(device_handler['ip'] + "_" + hostname + ".txt", "w")
        output.write("Hostname : " + hostname + "\n")
        output.write("IP : " + device_handler['ip'] + "\n")
        output.write(mac_result)
        output.close()
        switch_conn.cleanup()
    except NetMikoTimeoutException:
        print(device_handler['ip'] + " timed out!")
        logger.debug(device_handler['ip'] + " timed out!")
    except AuthenticationException:
        print('Wrong credentials for ' + device_handler['ip'])
        logger.debug('Wrong credentials for ' + device_handler['ip'])


my_user = input("Username: ")
my_pass = getpass("Password: ")
main()
