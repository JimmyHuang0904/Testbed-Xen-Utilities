#!/bin/bash
sudo losetup /dev/loop1 /mnt/vmdisk/ubuntu160401 
sudo losetup /dev/loop2 /mnt/vmdisk/ubuntu160402
sudo losetup /dev/loop3 /mnt/vmdisk/ubuntu160403
sudo losetup /dev/loop4 /mnt/vmdisk/ubuntu160404
sudo losetup /dev/loop5 /mnt/vmdisk/ubuntu

sudo xl create /etc/xen/ubuntu160401.cfg
sudo xl create /etc/xen/ubuntu160402.cfg
sudo xl create /etc/xen/ubuntu160403.cfg
sudo xl create /etc/xen/ubuntu160404.cfg

sudo modprobe usbip-core
sudo modprobe usbip-host
sudo usbipd -D
