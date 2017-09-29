#!/usr/bin/env python2

import sys
import time
import socket
import os

def init_raspi():
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

def get_position(name, port):
  for gpio in port:
    if gpio["name"] == name:
      return gpio["position"]

  return -1

def get_json_index(target_type, power_switch_num):
  index = 0
  for target_num in json_ref["controller"]:

    if target_num["type"] == target_type and \
       target_num["power_switch"] == power_switch_num:
      return index
    index += 1

  raise Exception("Index of target_id in JSON file cannot be found")

def write_to_json(data, path):
  import json
  from pprint import pprint
  with open(path, "w") as data_file:
    json.dump(data, data_file, sort_keys=True, indent=4, separators=(',', ': '))

def read_json(path):
  import json
  with open(path) as data_file:
    return json.load(data_file)

def get_target(target_id):
  if not int(target_id) in targets:
    targets[int(target_id)] = Controller(target_id)
  return targets[int(target_id)]

class Controller:

  def __init__(self, target_id):
    self.target_id = target_id
    self.power_switch_num = {}

  def set_target(self, port, portinfo, target_type, power_switch_num):
    if portinfo["name"] == "power":
      self.power = int(port)
    elif portinfo["name"] == "boot":
      self.boot = int(port)
    elif portinfo["name"] == "sim":
      self.sim = int(port)

    self.power_switch_num[portinfo["name"]] = (power_switch_num, target_type)

  # def declare(self):
  #   print "power:%d, boot:%d, sim:%d" %(self.power, self.boot, self.sim)
  #   print(self.power_switch_num)

  def set_boot_inverted(self, state):
    print "Target#%d: Gpio Boot %s" % (self.id, "Inverted" if state else "Normal")
    self.boot_inverted = state

  def switch_power(self, state):
    self.create_target(self.power_switch_num["power"])
    targets[target_id].output(self.power, state)

  def switch_boot(self, state):
    self.create_target(self.power_switch_num["boot"])
    targets[target_id].output(self.boot, state)

  def switch_sim(self, state):
    self.create_target(self.power_switch_num["sim"])
    targets[target_id].output(self.sim, state)

  def create_target(self, power_switch_num):
    if(power_switch_num[1] == 'usb_relay'):
      targets[target_id] = UsbRelayTarget(power_switch_num[0])
    # elif(power_switch_num[1] == 'raspberrypi'):
      # targets[target_id] = GpioTarget(power_switch_num[0])
    # elif(power_switch_num[1] == 'frilm-ed-pwrs01')
      # targets[target_id] = GpioTarget(power_switch_num[0])
    # elif(power_switch_num[1] == 'carmd-ed-lxlegato03')
      # targets[target_id] = MraaaTarget(power_switch_num[0])

class Target:
  def __check_gpio(self, gpio):
      if gpio < 0:
        raise Exception("Target#%d: Invalid GPIO %d" % (self.id, gpio))

  def set_boot_inverted(self, state):
    print "Target#%d: Gpio Boot %s" % (self.id, "Inverted" if state else "Normal")
    self.boot_inverted = state

  def is_boot_inverted(self):
    return self.boot_inverted

  def output(self, gpio, state):
    raise Exception("Not implemented")

  def input(self, gpio):
    raise Exception("Not implemented")

  def switch_power(self, state):
    print "Target#%d: Power %s (is %s)" \
      % (self.id, "On" if state else "Off", "Off" if self.input(self.power) else "On")
    self.output(self.power, state)

  def switch_boot(self, state):
    actual_state = not state
    if self.is_boot_inverted():
      actual_state = state

    print "Target#%d: Boot %s (is %s)" \
      % (self.id, "On" if actual_state else "Off", "Off" if self.input(self.boot) else "On")
    self.output(self.boot, actual_state)

  def switch_sim(self, state):
    if self.sim == -1:
      print "Target#%d: SIM switch is NOT SUPPORTED" % (self.id)
    else:
      self.__check_gpio(self.sim)
      print "Target#%d: SIM %s (is %s)" \
        % (self.id, "On" if state else "Off", "Off" if self.input(self.sim) else "On")
      self.output(self.sim, state)

class UsbRelayTarget(Target):

  path_to_json =  os.getenv('POWER_SWITCH_JSON','/home/jimmy/pythonWorkspace/power_switch.json')
  baudrate = 9600

  def __init__(self, id):

    import serial
    self.id = id

  def setup_env(self):
    self.json_data = read_json(self.path_to_json)

    index = get_json_index("usb_relay", self.id)
    self.device = self.json_data["controller"][index]
    self.open_port()
    self.current_state = self.device["overall_state"]
    self.check_devnum()

  def check_devnum(self):
    os.chdir("/sys/bus/usb/devices" + self.device["busnum"])
    os.chdir("..")
    with open('devnum', 'r') as devnumfile:
      devnum = int( devnumfile.read() )

      if devnum != self.device["devnum"]:
        self.initialize_relay()

        # Overwriting new devnum to JSON file
        self.device["devnum"] = devnum
        write_to_json(self.json_data, self.path_to_json)
      devnumfile.close()

  def open_port(self):
    import serial

    for file in os.listdir("/sys/bus/usb/devices" + self.device["busnum"]):
      if file.startswith("ttyUSB"):
        port = "/dev/" + file

        self.serial_ref = serial.Serial(port, self.baudrate)

  def initialize_relay(self):
    print "Initializing Usb Relay Device"
    self.serial_ref.write('\x50')
    time.sleep(1)
    self.serial_ref.write('\x51')
    time.sleep(1)

    self.next_state = 0x00
    self.set_state()

  def output(self, gpio, state):
    self.setup_env()

    time.sleep(1)

    bit = 1 << gpio

    self.current_state = self.device["overall_state"]

    if not self.current_state:
      if state:
        self.next_state = bit
      else:
        self.next_state = 0x00
    elif state:
      self.next_state =  bit | int(self.current_state, 16)
    else:
      self.next_state = ~bit & int(self.current_state, 16)

    self.serial_ref.write(chr(self.next_state))

    self.set_state(gpio)

  def set_state(self, gpio):
    self.device["overall_state"] = hex(ord(chr(self.next_state)))

    for ports in self.device["gpio"]:
      if self.next_state & 1 << gpio:
        ports[str(gpio)][0]["state"] = 1
      else:
        ports[str(gpio)][0]["state"] = 0

    write_to_json(self.json_data, self.path_to_json)

targets = {}

config = os.getenv("POWER_CONFIG", socket.gethostname())

path_to_json =  os.getenv('POWER_SWITCH_JSON','/home/jimmy/pythonWorkspace/power_switch.json')

json_ref = read_json(path_to_json)

for controller_array in json_ref["controller"]:
  for gpio in controller_array["gpio"]:
    for ports in gpio:
      for port_info in gpio[ports]:
        target = get_target(port_info["target_id"])
        target.set_target(ports, port_info, controller_array["type"], controller_array["power_switch"])

if len(sys.argv) < 3:
  sys.stderr.write('Usage: <target> <fn> <?boot_inverted 1 or 0>\n')
  sys.exit(1)

target_id = int(sys.argv[1])
fn = sys.argv[2]

boot_inverted = True
if len(sys.argv) >= 4:
  boot_inverted = (sys.argv[3] == "1")

target = get_target(target_id)

print(boot_inverted)
# target.set_boot_inverted(boot_inverted)

if fn == "reboot":
  target.switch_boot(True)
  target.switch_power(False)
  time.sleep(1)
  target.switch_power(True)

if fn == "recovery":
  target.switch_boot(False)
  target.switch_power(False)
  time.sleep(1)
  target.switch_power(True)

elif fn == "on":
  target.switch_boot(True)
  target.switch_power(True)

elif fn == "off":
  target.switch_power(False)

elif fn == "power" or fn == "sim":
  arg_state = sys.argv[3]
  if arg_state == "on":
    state = True
  elif arg_state == "off":
    state = False
  else:
    raise Exception("Invalid state %s" % arg_state)

  if fn == "power":
    target.switch_power(state)
  elif fn == "sim":
    target.switch_sim(state)
