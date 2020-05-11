#!/bin/bash
exec qemu-system-x86_64 --enable-kvm -name $1 \
 	-smp 2,sockets=1,cores=1,threads=2 \
	-cpu host \
	-m $2G -usbdevice tablet -display vnc=:$3 \
	-device e1000,netdev=net0,mac=00:00:00:00:00:$4 -netdev tap,id=net0,script=machine-disk/rede.sh \
	-drive file=machine-disk/$5.img,if=virtio -monitor tcp:127.0.0.1:$6,server,nowait;
	

