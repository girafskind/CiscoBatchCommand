# Cisco Batch Command
This Python script will help you with running commands on several Cisco Catalyst devices.
It will run each connection in separate thread, it will batch together 100 commands by default. This can be changed.

## Requirements
See requirements.txt

## Running the code
Running the code is easy:

    python3 main.py

Then enter username and password which will authorize access to the devices.
By default, it will gather _**show ver | i System serial number**_ and save it in seperate files.

If you want another command, add it in quotes after _main.py_.

E.g.:

    python3 main.py "show mac addresses"

## devices.csv
The CSV file contains the IP-address of the devices you wish to connect to.
First value after the IP is for custom commands, if nothing is noted there, the default command is used.

## Logging
The program will create a logfile, describing which devices that were connection attempts to, and which commands that where sent.

# TO-DO
 - [ ] Creating possibility to push config set