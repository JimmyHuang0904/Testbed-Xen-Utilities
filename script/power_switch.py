import serial
import time
import string
import sys
import os
import json
from pprint import pprint

pathToJson = "/home/jimmy/pythonWorkspace/power_switch/power_switch.json"
baudrate = 9600

class RelayControl:

    def initialize_relay(self, serialref):
        serialref.write('\x50')
        time.sleep(0.5)
        serialref.write('\x51')
        time.sleep(0.5)

class Target(RelayControl):

    def __init__(self, path):
        ''' Read JSON file configurations '''
        with open(path) as data_file:    
            self.json_data = json.load(data_file)

    def write_to_json(self, data):
        with open(pathToJson, "w") as data_file:
            json.dump(data, data_file)

    def open_port(self, target_id, json_data):
        for file in os.listdir("/sys/bus/usb/devices" + json_data["bus"][target_id-1]["num"]):
            if file.startswith("ttyUSB"):
                port = "/dev/" + file
                self.serialref = serial.Serial(port, baudrate)

    def dev_num_check(self, target_id, json_data):
        ''' Change directory to where devnum textfile is and save it to self.devnum'''
        # print(json_data["bus"][ target_id - 1 ]["num"])
        os.chdir("/sys/bus/usb/devices" + json_data["bus"][ target_id - 1 ]["num"])
        os.chdir("..")
        devnumfile = open('devnum', 'r')
        devnum = int( devnumfile.read() )

        if devnum != json_data["bus"][ target_id - 1 ]["devnum"]:
            # Running initializing sequence
            print("Initializing device")
            self.initialize_relay(self.serialref)

            # Overwriting new devnum to JSON file
            json_data["bus"][ target_id-1 ]["devnum"] = devnum
            self.write_to_json(json_data)
        devnumfile.close()

# main
target_id = int(sys.argv[1])

# Open JSON file for reading
# with open(pathToJson) as data_file:    
#     json_data = json.load(data_file)

var = Target(pathToJson)

var.open_port(target_id, var.json_data)

var.dev_num_check(target_id, var.json_data)

# Get /dev/ttyUSB* 
# for file in os.listdir("/sys/bus/usb/devices/1-1/1-1:1.0"):
#     if file.startswith("ttyUSB"):
#         port = "/dev/" + file

# print (port)
# baudrate = 9600

# Compare devnum with JSON file, if not the same, we initialize the device and set the devnum onto the JSON file
# os.chdir("/sys/bus/usb/devices/1-1")
# devnumfile = open('devnum', 'r')
# devnum = devnumfile.read()
# devnumfile.close()
# print(var.devnum)

# print(data["devnum"])

# serialref=serial.Serial(port, baudrate)
# serialref.close()

# #this part of the code does initialization
# time.sleep(0.5)
# serialref.write('\x50')
# time.sleep(0.5)
# serialref.write('\x51')
# time.sleep(0.5)

# serialref.write('\x05')
# time.sleep(1)
# serialref.write('\x06')


# if len(sys.argv) < 3:
#   sys.stderr.write('Usage: <target> <fn> <?boot_inverted 1 or 0>\n')
#   sys.exit(1)

# target_id = int(sys.argv[1])
# fn = sys.argv[2]

# boot_inverted = True
# if len(sys.argv) >= 4:
#   boot_inverted = (sys.argv[3] == "1")






# def bootswitch():
#     serialref.write('\x05')
#     time.sleep(1)
#     serialref.write('\x06')
#     return
# def powercycle():
#     serialref.write('\x01')
#     time.sleep(1)
#     serialref.write('\x00')
#     return
    # # hexwrite = sys.argv[1]
    # # print(hexwrite)
    # # table = string.maketrans("abcdefABCDEF", "jklmnoJKLMNO")
    # bootswitch()
    # # hexwrite = hexwrite.translate(table)
    # # if hexwrite == 'boot':
    # #     bootswitch()
    # # elif hexwrite == 'cycle':
    # #     powercycle()
    # # else:
    # #     serialref.write('\\'+hexwrite)
    # serialref.close()
