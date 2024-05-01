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
from datetime import datetime, timedelta
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
        csv_data = list(csv.reader(devices, delimiter=';'))

    dict_of_devices = convert_csvdata_to_dict(csv_data)

    device_commands_list = []
    for key, list_of_commands in dict_of_devices.items():
        for command in list_of_commands:
            device_commands_list.append([key,command])

    # Create queues of threads, divided into lists of 100
    list_of_queues = queue_threads(device_commands_list)
    # Run each thread queue at the time
    thread_time = run_threads(list_of_queues)

    print("\nOperation took: {}".format(datetime.now() - start_time))
    input("\nPress Enter to continue...")


def convert_csvdata_to_dict(csv_data_tobe_converted: list) -> dict:
    """
    Convert the list of devices into a dictionary
    :param csv_data_tobe_converted: List with list of devices
    :return: Dictionary of devices
    """
    device_dict = {}

    for entry in csv_data_tobe_converted:
        device_ip = entry[0]
        commands_for_device = []
        if len(entry[1]) > 0:
            commands_for_device.append(entry[1])
        else:
            commands_for_device.append(CONFIGSET)

        if device_ip in device_dict.keys():
            device_dict[device_ip] += commands_for_device
        else:
            device_dict[device_ip] = commands_for_device

    return device_dict


def queue_threads(devices_to_queue: list, max_concurrent_threads=100) -> list:
    """
    Queue threads in batches of specific number of threads, default is 100.
    :param devices_to_queue: The device to be added
    :param max_concurrent_threads: Number of threads to queue
    :return: List of queues with threads
    """
    thread_queue = []
    thread_queue_list = []
    while len(devices_to_queue) > 0:
        while len(thread_queue) <= max_concurrent_threads:
            if len(devices_to_queue) > 0:
                device_from_queue = devices_to_queue.pop(0)
                thread_queue.append(threading.Thread(target=runcommand, args=(device_from_queue,)))
            else:
                break
        thread_queue_list.append(thread_queue)
        thread_queue = []

    return thread_queue_list


def run_threads(thread_queue: list) -> timedelta:
    """
    Start the given thread queue
    :param thread_queue: The thread queue list to start
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


def runcommand(device_to_configure: str):
    """
    Function for pushing out command to device
    :param device_to_configure: String containing the IP of the device
    :return: Nothing
    """
    device_handler = {'username': my_user, 'password': my_pass, 'ip': device_to_configure[0],
                      'device_type': "cisco_ios"}
    command_to_send = device_to_configure[1]
    try:
        switch_conn = ConnectHandler(**device_handler)
        logger.debug('Handler connected to ' + device_handler['ip'])
        print("Handler connected")
        hostname = switch_conn.find_prompt().replace("#", "")
        cmd_result = switch_conn.send_command(command_to_send)

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
