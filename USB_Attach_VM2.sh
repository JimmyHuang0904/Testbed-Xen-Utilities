#!/bin/bash

echo "$(date)" >> /tmp/USB_Auto_Attach_Logs
echo "USB_Attach_VM2" >> /tmp/USB_Auto_Attach_Logs

HOST_IP="$(ifconfig | grep -A 1 'xenbr0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1)"
MAPPING_PWD=/home/xentest/Documents/Mapping
#VM_MAC_ADDRESS=($(sudo xl network-list "$VM_NAME" | grep -E -o '[[:xdigit:]]{2}(:[[:xdigit:]]{2}){5}'))
#VM_IP=($(ip neighbor | grep "$VM_MAC_ADDRESS" | cut -d" " -f1)) #this doesnt work well because ip neighbor doesnt always return right

#Number of Bus ID for $IPToSet
#NumIDs=$(awk '{print NF}' ~/Documents/Mapping | sort -nu | tail -n 1)
SSH_NO_CHECK="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

for (( VM_NUM=1; VM_NUM<=4; VM_NUM++))
do
    VM_NAME=$(awk -v i=$VM_NUM 'FNR == i {print $1}' ~/Documents/Mapping)
    VM_MAC_ADDRESS=($(sudo xl network-list "$VM_NAME" | grep -E -o '[[:xdigit:]]{2}(:[[:xdigit:]]{2}){5}'))
    VM_IP=($(ip neighbor | grep "$VM_MAC_ADDRESS" | cut -d" " -f1))
    NumIDs=$(awk -v i=$VM_NUM 'FNR == i {print NF}' ~/Documents/Mapping)

    echo "VM_NAME@VM_IP = $VM_NAME@$VM_IP    VM_MAC_ADDRESS = $VM_MAC_ADDRESS    NumIDs = $NumIDs"

    ssh $SSH_NO_CHECK -t jenkins@$VM_IP "sudo modprobe vhci-hcd" &> /dev/null

    for (( j=2; j <= $NumIDs; j++))
    do
        BusID=$(awk -v i="$VM_NUM" -v j="$j" 'FNR == i {print $j}' ~/Documents/Mapping)
#        echo "BusID = $BusID"

        sudo usbip unbind -b $BusID &> /dev/null
        sudo usbip bind -b $BusID &> /dev/null

        if [ $? -eq 0 ]; then
            BUS_DESC=$(sudo usbip list -l | sed -n "/$BusID/{n;p;}")
            echo "Attached $BUS_DESC to the VM"
            ssh $SSH_NO_CHECK -t jenkins@$VM_IP "sudo usbip attach --remote=$HOST_IP --busid=$BusID" &> /dev/null && echo "Attached the BusID $BusID to the VM $VM_NAME@$VM_IP" >> /tmp/USB_Auto_Attach_Logs
        fi
    done

done

#for (( i=2; i <= $NumIDs; i++))
#do
#    BusID=$(awk -v i=$i '{print $i}' ~/Documents/Mapping | head -n 1)
#    echo "Binding $BusID to VM $VM_NAME@$VM_IP"
#    sudo usbip unbind -b $BusID &> /dev/null
#    sudo usbip bind -b $BusID
#    if [ $? -eq 0 ]; then
#        ssh $SSH_NO_CHECK -t jenkins@$VM_IP "sudo usbip attach --remote=$HOST_IP --busid=$BusID" && echo "Attached the BusID $BusID to the VM $VM_NAME@$VM_IP" >> /tmp/USB_Auto_Attach_Logs
#    fi
#done
