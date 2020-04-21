import socket
# from pickle import loads
from cPickle import dumps, loads
import cv2 as cv
import numpy as np
import os
import time

_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_connection.bind(('10.0.0.116', 4445))
_connection.listen(1)
while True:
	start = time.time()
	connection, client = _connection.accept()
	connection.send('OK'.encode('utf-8'))
	img = []
	while True:
		packet = connection.recv(10024)
		if not packet:
			break
		img.append(packet)        
	img = loads(b"".join(img))
	cv.imshow('Ragnarok', img)
	cv.waitKey(1)
	
	hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
	lower_range = np.array([110,140,160])
	upper_range = np.array([130,255,255])
	mask = cv.inRange(hsv, lower_range, upper_range)
	try:
		coord = cv.findNonZero(mask)
		x, y = coord[50][0]
	except:
		# print('Elapsed - {}'.format(time.time() - start))
		continue
	os.system('vncdotool -s localhost move {} {} click 1'.format(x, y))
	os.system('echo mouse_button {}|nc -N 127.0.0.1 4444 > /dev/null 2'.format(1))
	time.sleep(0.2)
	os.system('echo mouse_button {}|nc -N 127.0.0.1 4444 > /dev/null 2'.format(0))
	time.sleep(3)
	# print('Elapsed - {}'.format(time.time() - start))