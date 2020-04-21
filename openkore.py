import cv2 as cv
import numpy as np
import time
import os


while True:
	start = time.time()
	os.system('echo screendump /home/eduardo/Documentos/refactor/screenshot.png | nc -N 127.0.0.1 4444 > /dev/null 2')
	img = cv.imread('screenshot.png')
	hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
	lower_range = np.array([110,140,160])
	upper_range = np.array([130,255,255])
	mask = cv.inRange(hsv, lower_range, upper_range)
	try:
		coord = cv.findNonZero(mask)
		x, y = coord[50][0]
	except:
		print('Elapsed - {}'.format(time.time() - start))
		continue
	os.system('vncdotool -s localhost move {} {} click 1'.format(x, y))
	os.system('vncdotool -s localhost move {} {} click 1'.format(x, y))
	os.system('echo mouse_button {}|nc -N 127.0.0.1 4444 > /dev/null 2'.format(1))
	time.sleep(0.2)
	os.system('echo mouse_button {}|nc -N 127.0.0.1 4444 > /dev/null 2'.format(0))
	time.sleep(3)
	print('Elapsed - {}'.format(time.time() - start))

