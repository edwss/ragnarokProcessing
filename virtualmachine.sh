#!/bin/bash
exec qemu-system-x86_64 --enable-kvm \
 	-smp 4,sockets=1,cores=2,threads=2 \
	-m 2G -device virtio-vga,virgl=on -usbdevice tablet -display vnc=127.0.0.1:0 -display sdl,gl=on \
	-device e1000,netdev=net0,mac=00:00:00:00:00:01 -netdev tap,id=net0,script=rede.sh \
	-drive file=windows10,format=raw -monitor tcp:127.0.0.1:4444,server,nowait;
