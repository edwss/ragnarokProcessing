#!/bin/bash
exec qemu-system-x86_64 --enable-kvm \
 	-smp 2,sockets=1,cores=1,threads=2 \
	-cpu host,-hypervisor,migratable=no,+invtsc,kvm=off \
	-m 2G -display vnc=127.0.0.1:$1 -display gtk,gl=on \
	-device e1000,netdev=net0,mac=00:00:00:00:00:$2 -netdev tap,id=net0,script=rede.sh \
	-drive file=machine-disk/$3.img,format=raw -monitor tcp:127.0.0.1:$4,server,nowait;


