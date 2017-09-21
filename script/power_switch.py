#!/usr/bin/env python2

import sys
import time
import socket
import os

def write_to_json(data, path):
  import json
  from pprint import pprint
  with open(path, "w") as data_file:
    json.dump(data, data_file, sort_keys=True, indent=4, separators=(',', ': '))

def read_json(path):
  import json
  with open(path) as data_file:
    return json.load(data_file)

class Target:
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

  path_to_json =  os.getenv('POWER_SWITCH_JSON','/tmp/power_switch.json')
  baudrate = 9600

  def __init__(self, id, power, boot, sim=-1):

    import json
    import serial

    self.id = id
    self.power = power
    self.boot = boot
    self.sim = sim

    self.json_data = read_json(self.path_to_json)

    self.device = self.json_data["target"][self.id - 1]

    self.open_port()

    self.current_state = self.device["overall_state"]

    self.get_position()

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

  def get_position(self):

    for functions in self.device["gpio"]:
      if functions["name"] == 'power':
        self.power = functions["position"]
      elif functions["name"] == 'boot':
        self.boot = functions["position"]
      elif functions["name"] == 'sim':
        self.sim = functions["position"]
      else:
        raise Exception("GPIO missing keyword \"name\" in JSON file")

  def open_port(self):
    import serial

    for file in os.listdir("/sys/bus/usb/devices" + self.device["busnum"]):
      if file.startswith("ttyUSB"):
        port = "/dev/" + file
        print(port)

        self.serial_ref = serial.Serial(port, self.baudrate)

  def initialize_relay(self):
    print "Initializing Usb Relay Device"
    self.serial_ref.write('\x50')
    time.sleep(1)
    self.serial_ref.write('\x51')
    time.sleep(1)

    self.next_state = chr(0x00)
    self.set_state()

  def input(self, gpio):
    state = self.device["gpio"][gpio]["state"]
    return state

  def output(self, gpio, state):
    time.sleep(1)

    bit = 1 << gpio

    self.current_state = self.device["overall_state"]

    if not self.current_state:
      if state:
        self.next_state = chr(bit)
      else:
        self.next_state = chr(0x00)
    elif state:
      self.next_state = chr( bit | int(self.current_state, 16))
    else:
      self.next_state = chr(~bit & int(self.current_state, 16))

    self.serial_ref.write(self.next_state)
    self.set_state()

  def set_state(self):
    self.device["overall_state"] = hex(ord(self.next_state))
    write_to_json(self.json_data, self.path_to_json)

targets = {}

hostname = os.getenv("POWER_CONFIG", socket.gethostname())

print "hostname: %s" % (hostname)

if hostname == "usb_relay":
  targets[1] = UsbRelayTarget(1, 0, 1, 2)
else:
  raise Exception("Hostname has no permission")

if len(sys.argv) < 3:
  sys.stderr.write('Usage: <target> <fn> <?boot_inverted 1 or 0>\n')
  sys.exit(1)

target_id = int(sys.argv[1])
fn = sys.argv[2]

boot_inverted = True
if len(sys.argv) >= 4:
  boot_inverted = (sys.argv[3] == "1")

if not target_id in targets:
  sys.stderr.write('Target %d unknown\n' % target_id)
  sys.exit(1)

target = targets[target_id]
target.set_boot_inverted(boot_inverted)

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
