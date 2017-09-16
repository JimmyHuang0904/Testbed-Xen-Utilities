#!/bin/bash

echo "$(date)" >> /tmp/USB_Auto_Attach_Logs
echo "USB_Attach_VM2" >> /tmp/USB_Auto_Attach_Logs

HOST_IP="$(ifconfig | grep -A 1 'xenbr0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1)"
MAPPING_PWD=/home/xentest/Documents/Mapping

SSH_NO_CHECK="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

for (( VM_NUM=1; VM_NUM<=4; VM_NUM++))
do
    VM_NAME=$(awk -v i=$VM_NUM 'FNR == i {print $1}' $MAPPING_PWD)
    VM_MAC_ADDRESS=($(sudo xl network-list "$VM_NAME" | grep -E -o '[[:xdigit:]]{2}(:[[:xdigit:]]{2}){5}'))
    VM_IP=($(ip neighbor | grep "$VM_MAC_ADDRESS" | cut -d" " -f1))
    NUM_IDS=$(awk -v i=$VM_NUM 'FNR == i {print NF}' $MAPPING_PWD)
    echo "VM_NAME@VM_IP = $VM_NAME@$VM_IP    VM_MAC_ADDRESS = $VM_MAC_ADDRESS    NUM_IDS = $NUM_IDS"

    ssh $SSH_NO_CHECK -t jenkins@$VM_IP "sudo modprobe vhci-hcd" &> /dev/null

    for (( j=2; j <= $NUM_IDS; j++))
    do
        BUS_ID=$(awk -v i="$VM_NUM" -v j="$j" 'FNR == i {print $j}' $MAPPING_PWD)
        sudo usbip bind -b $BUS_ID &> /dev/null

        if [ $? -ne 0 ]; then

            #Checks if usb device was already bound manually and attach to the VM
            ERROR_STR=$(sudo usbip bind -b $BUS_ID 2>&1)
            if [ "$ERROR_STR" = "usbip: error: device on busid $BUS_ID is already bound to usbip-host" ]; then
               ssh $SSH_NO_CHECK -t jenkins@$VM_IP "sudo usbip attach --remote=$HOST_IP --busid=$BUS_ID" &> /dev/null && echo "Atasdtached the BUS_ID $BUS_ID to the VM $VM_NAME@$VM_IP" >> /tmp/USB_Auto_Attach_Logs
            fi
        else
            BUS_DESC=$(sudo usbip list -l | sed -n "/$BUS_ID/{n;p;}")
            echo "Attached $BUS_DESC to the VM"
            ssh $SSH_NO_CHECK -t jenkins@$VM_IP "sudo usbip attach --remote=$HOST_IP --busid=$BUS_ID" &> /dev/null && echo "Attached the BUS_ID $BUS_ID to the VM $VM_NAME@$VM_IP" >> /tmp/USB_Auto_Attach_Logs
        fi
    done
done
