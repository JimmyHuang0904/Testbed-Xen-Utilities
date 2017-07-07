#!/bin/bash
sudo losetup /dev/loop1 /mnt/vmdisk/ubuntu16_04_1 
sudo losetup /dev/loop2 /mnt/vmdisk/ubuntu16_04_2
sudo losetup /dev/loop3 /mnt/vmdisk/ubuntu160403
sudo losetup /dev/loop4 /mnt/vmdisk/ubuntu

sudo modprobe usbip-core
sudo modprobe usbip-host
sudo usbipd -D
