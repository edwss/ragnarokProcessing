import socket
# from pickle import loads
from cPickle import dumps, loads
import cv2 as cv
import numpy as np
import os
import time
import sys 

socket_port = int(sys.argv[1])
vnc_port = sys.argv[2]
qemu_port = sys.argv[3]

print('Started running')
last_attack = time.time()
_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_connection.bind(('10.0.0.116', socket_port))
_connection.listen(1)
while True:
	start = time.time()
	try:
		connection, client = _connection.accept()
		connection.send('OK'.encode('utf-8'))
		img = []
		while True:
			packet = connection.recv(10024)
			if not packet:
				break
			img.append(packet)
		try:        
			img = loads(b"".join(img))
			cv.imshow('Ragnarok', img)
			cv.waitKey(1)
			
			hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
			lower_range = np.array([100,250,100])
			upper_range = np.array([130,255,255])
			mask = cv.inRange(hsv, lower_range, upper_range)
			try:
				coord = cv.findNonZero(mask)
				x, y = coord[50][0]
			except:
				if time.time() > last_attack + 6:
					os.system('vncdotool -s localhost:{} key f2 click 1'.format(vnc_port))
					last_attack = time.time()
					continue
				# print('Elapsed - {}'.format(time.time() - start))
				continue
			os.system('vncdotool -s localhost:{} move {} {} click 1'.format(vnc_port ,x, y))
			os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(qemu_port, 1))
			time.sleep(0.2)
			os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(qemu_port ,0))
			time.sleep(3.5)
			last_attack = time.time()
			print('Elapsed - {}'.format(time.time() - last_attack))
		except:
			print('Error with received image')
	except:
		print('Closed connection')