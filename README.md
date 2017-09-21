Testbed-Xen-Utilities
=========================
Testbed automation requires many setup and hardware configurations. For the testbed that we are creating, 
these scripts will help aid in the overall automation of a testing cycle and make our software developers
live with less frustration :). 

These utilities are written to be modular and scalable. They include many parts of a testbench such as 
relays that can be controlled in two ways:

*[ICStation 4 Channel Relays](http://www.icstation.com/icstation-micro-channel-relay-module-control-relay-module-p-4012.html)
uses /script/power_switch.py which has the following protocol:
```
$python power_switch.py <target_id> <function> <boot inverted ? 1 : 0 >
```
Functions that has been implemented so far: `reboot`, `recovery`, `on`, `off`, `sim on/off`, `power on/off`
