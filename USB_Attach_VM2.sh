#!/bin/bash
Host_IP="$(ifconfig | grep -A 1 'xenbr0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1)"
echo "$(date)" >> /tmp/USB_Auto_Attach_Logs
echo "USB_Attach_VM2" >> /tmp/USB_Auto_Attach_Logs
#BusID=($(echo "$DEVPATH" | grep -o '[[:digit:]]*\-[[:digit:]]*\.[[:digit:]]*'))
VMToSet=($(grep "$BusID" /home/xentest/Documents/Mapping | grep -o "[[:alnum:]]*"))
#VMToSet="${VMToSet[0]}"
MacAddress=($(sudo xl network-list "$VMToSet" | grep -E -o '[[:xdigit:]]{2}(:[[:xdigit:]]{2}){5}'))
IPToSet=($(ip neighbor | grep "$MacAddress" | cut -d" " -f1)) #this doesnt work well because ip neighbor doesnt always return right

#Number of Bus ID for $IPToSet
NumIDs=$(awk '{print NF}' ~/Documents/Mapping | sort -nu | tail -n 1)

for (( i=2; i <= $NumIDs; i++))
do
    BusID=$(awk -v i=$i '{print $i}' ~/Documents/Mapping | head -n 1)
    echo "Binding $BusID to VM $VMToSet@$IPToSet"
    sudo usbip bind -b $BusID    
    ssh -o StrictHostKeyChecking=no -t jenkins@$IPToSet "sudo usbip attach --remote=$Host_IP --busid=$BusID" && echo "Attached the BusID $BusID to the VM $VMToSet@$IPToSet" >> /tmp/USB_Auto_Attach_Logs
done
