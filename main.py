#!/usr/bin/python
# Cisco IOS bulk command sender
# Takes CSV file with IPs, logs into device and runs either the CONFIGSET string or the command in quotes.
# python3 main.py "show version" - Will run show version on all devices
# python3 main.py - Will run the command set in the CONFIGSET variable
# Created 15th of June 2020
# Bo Vittus Mortensen
# Version 1.4

import csv
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

    with open('devices.csv', 'r') as devices:
        data = list(csv.reader(devices, delimiter=';'))

    # Create queues of threads, divided into lists of 100
    queues = queue_threads(data)
    # Run each thread queue at the time
    thread_time = run_threads(queues)

    print("\nOperation took: {}".format(datetime.now() - start_time))
    input("\nPress Enter to continue...")


def queue_threads(devices_to_queue, threads=100):
    """
    Queue threads in batches of specific number of threads, default is 100.
    :param devices_to_queue: The device to be added
    :param threads: Number of threads to queue
    :return: List of queues with threads
    """
    thread_queue = []
    thread_queue_list = []
    while len(devices_to_queue) > 0:
        while len(thread_queue) <= threads:
            if len(devices_to_queue) > 0:
                command = devices_to_queue.pop(0)
                thread_queue.append(threading.Thread(target=runcommand, args=(command,)))
            else:
                break
        thread_queue_list.append(thread_queue)
        thread_queue = []

    return thread_queue_list


def run_threads(thread_queue):
    """
    Start the given thread queue
    :param thread_queue: The thread queue to start
    :return: Time the whole operation took
    """
    start_time = datetime.now()
    for queue in thread_queue:
        for thread in queue:
            thread.start()
        for thread in queue:
            thread.join()
    end_time = datetime.now()
    duration = end_time - start_time
    return duration


def runcommand(devicestring):
    """
    Function for pushing out command to device
    :param devicestring: String containing the IP of the device
    :return: Nothing
    """
    device_handler = {'username': my_user, 'password': my_pass, 'ip': devicestring[0],
                      'device_type': "cisco_ios"}
    try:
        switch_conn = ConnectHandler(**device_handler)
        logger.debug('Handler connected to ' + device_handler['ip'])
        print("Handler connected")
        hostname = switch_conn.find_prompt().replace("#", "")
        cmd_result = switch_conn.send_command(CONFIGSET)

        output = open(device_handler['ip'] + "_" + hostname + ".txt", "w")
        output.write("#" * len(" Hostname : " + hostname + " ")+"\n")
        output.write(" Hostname : " + hostname + "\n")
        output.write(" IP : " + device_handler['ip'] + "\n")
        output.write("#" * len(" Hostname : " + hostname + " ")+"\n")
        output.write(cmd_result+"\n")
        output.close()
        switch_conn.cleanup()
    except NetMikoTimeoutException:
        print(device_handler['ip'] + " timed out!")
        logger.debug(device_handler['ip'] + " timed out!")
    except NetmikoAuthenticationException:
        print('Wrong credentials for ' + device_handler['ip'])
        logger.debug('Wrong credentials for ' + device_handler['ip'])


if __name__ == '__main__':
    my_user = input("Username: ")
    my_pass = getpass("Password: ")

    if len(sys.argv) > 1:
        CONFIGSET = sys.argv[1]
    main()
