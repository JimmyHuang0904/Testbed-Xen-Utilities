#!/bin/bash
USER=jenkins

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

echo "NumIDs + 1 (Including hostname)  = $NumIDs"

for (( i=2; i <= NumIDs; i++))
do
    sudo usbip bind -b $(awk -v i=$i '{print $i }' ~/Documents/Mapping | head -n 1)
done

echo "Host_IP = $Host_IP"
echo "VMToSet = $VMToSet"
echo "MacAddress = $MacAddress"
echo "IPToSet = $IPToSet"

ssh -o StrictHostKeyChecking=no -l $USER@$IPToSet

#for (( i=2; i <= NumIDs; i++))
#do
    
#done
#ssh -t jenkins@$IPToSet "sudo usbip --port | grep $BusID" && { echo "ERROR: The BusID $BusID has already been attached to the VM $VMToSet@$IPToSet" >> /tmp/USB_Auto_Attach_Logs; exit 1; }
#usbip bind -b "$BusID" || { echo "Error binding the BusID $BusID" >> /tmp/USB_Auto_Attach_Logs; exit 1; }
#ssh -t jenkins@$IPToSet "sudo usbip --attach  $Host_IP -b $BusID" && echo "Attached the BusID $BusID to the VM $VMToSet@$IPToSet" >> /tmp/USB_Auto_Attach_Logs
