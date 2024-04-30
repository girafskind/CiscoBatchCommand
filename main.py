#!/usr/bin/python
# Cisco IOS bulk command sender
# Takes CSV file with IPs, logs into device and runs either the CONFIGSET string or the command in quotes.
# python3 main.py "show version" - Will run show version on all devices
# python3 main.py - Will run the command set in the CONFIGSET variable
# Created 15th of June 2020
# Updated 30th of April 2024
# Bo Vittus Mortensen
# Version 1.3

import threading
import logging
import sys
from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException, NetMikoTimeoutException
from datetime import datetime
from getpass import getpass

# Default command
CONFIGSET = "show ver | i System serial number"

logger = logging.getLogger('netscript')
hdlr = logging.FileHandler('status.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


def main():
    logger.debug(f'Executing {CONFIGSET} on devicelist')
    start_time = datetime.now()
    thread_list = list()

    with open('devices.csv', 'r') as devices:
        for line in devices:
            thread_list.append(threading.Thread(target=runcommand, args=(line,)))

    # Start all threads crated
    for thread in thread_list:
        thread.start()

    # Wait for all threads to complete
    for thread in thread_list:
        thread.join()

    print("\nOperation took: {}".format(datetime.now() - start_time))
    input("\nPress Enter to continue...")


def runcommand(devicestring):
    device_handler = {'username': my_user, 'password': my_pass, 'ip': devicestring.split(";")[0],
                      'device_type': "cisco_ios"}
    try:
        switch_conn = ConnectHandler(**device_handler)
        logger.debug('Handler connected to ' + device_handler['ip'])
        print("Handler connected")
        hostname = switch_conn.find_prompt().replace("#", "")
        mac_result = switch_conn.send_command(CONFIGSET)

        output = open(device_handler['ip'] + "_" + hostname + ".txt", "w")
        output.write("Hostname : " + hostname + "\n")
        output.write("IP : " + device_handler['ip'] + "\n")
        output.write(mac_result+"\n")
        output.close()
        switch_conn.cleanup()
    except NetMikoTimeoutException:
        print(device_handler['ip'] + " timed out!")
        logger.debug(device_handler['ip'] + " timed out!")
    except NetmikoAuthenticationException:
        print('Wrong credentials for ' + device_handler['ip'])
        logger.debug('Wrong credentials for ' + device_handler['ip'])


my_user = input("Username: ")
my_pass = getpass("Password: ")

if len(sys.argv) > 1:
    CONFIGSET = sys.argv[1]

print(CONFIGSET)
main()
