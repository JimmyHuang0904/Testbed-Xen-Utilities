import serial
import time
import string
import sys
import os
import json

pathToJson = "/home/jimmy/pythonWorkspace/power_switch/power_switch.json"
baudrate = 9600

class RelayControl:

    def initialize_relay(self, serialref):
        serialref.write('\x50')
        time.sleep(0.5)
        serialref.write('\x51')
        time.sleep(0.5)

    def power_off(self, serialref):
        serialref.write('0x08')
class Target(RelayControl):

    def __init__(self, path):
        ''' Read JSON file configurations '''
        with open(path) as data_file:    
            self.json_data = json.load(data_file)

    def set_target_id(self, target_id):
        self.target_id = target_id

    def write_to_json(self, data):
        with open(pathToJson, "w") as data_file:
            json.dump(data, data_file)

    def set_polarity_inverted(self, state):
        self.polarity_inverted = state

    # def is_polarity_inverted(self, asdf):
        # return self.polarty_inverted

    def open_port(self):
        for file in os.listdir("/sys/bus/usb/devices" + self.json_data["bus"][self.target_id - 1]["num"]):
            if file.startswith("ttyUSB"):
                port = "/dev/" + file
                self.serialref = serial.Serial(port, baudrate)

    def dev_num_check(self):
        ''' Change directory to where devnum textfile is and save it to self.devnum'''
        os.chdir("/sys/bus/usb/devices" + self.json_data["bus"][self.target_id - 1]["num"])
        os.chdir("..")
        devnumfile = open('devnum', 'r')
        devnum = int( devnumfile.read() )

        if devnum != self.json_data["bus"][self.target_id - 1]["devnum"]:
            # Running initializing sequence
            print("Initializing device")
            self.initialize_relay(self.serialref)

            # Overwriting new devnum to JSON file
            self.json_data["bus"][self.target_id - 1]["devnum"] = devnum
            self.write_to_json(self.json_data)
        devnumfile.close()

# main
if len(sys.argv) < 3:
    sys.stderr.write('Usage: <target> <fn> <?boot_inverted 1 or 0>\n')
    sys.exit(1)

target_id = int(sys.argv[1])
fn = sys.argv[2]

polarity_inverted = True
if len(sys.argv) >= 4:
    polarity_inverted = (sys.argv[3] == "1")

var = Target(pathToJson)

var.set_target_id(target_id)

var.open_port()

# var.is_polarity_inverted(var.serialref)

var.dev_num_check()

if fn == "off":
    var.power_off(var.serialref)

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
