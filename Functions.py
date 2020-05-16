import cv2 as cv
import numpy as np
import time
import os
from pickle import loads,dumps
import math
import logging
import telegram
import threading
import subprocess

machines = ''

def searchDistance(img, bot_name):
	start_time = time.time()
	hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
	lower_range = np.array([100,250,100])
	upper_range = np.array([130,255,255])
	mask = cv.inRange(hsv, lower_range, upper_range)
	try:
		coord = cv.findNonZero(mask)
		if coord is not None:
			distance = 1000
			origin = (407, 305)
			for i in range(0,len(coord)):
				distance_teste = math.sqrt(((origin[0] - coord[i][0][0])**2)+((origin[1] - coord[i][0][1])**2))
				if distance > distance_teste:
					click_point = coord[i][0]
					distance = distance_teste
			logging.info('Ended processing in : {} - distance : {}'.format(time.time() - start_time, distance))
			for machine in machines:
				if machine['bot_name'] == bot_name:
					vnc_port = machine['vnc_port']
					qemu_port = machine['qemu_port']
					click_point = checkClick(click_point)
					if checkClick(click_point) is not None:
						click(vnc_port, qemu_port, click_point[0], click_point[1])
						if distance > 120:
							time.sleep(2.5)
						else:
							time.sleep(1.5)
						machine['last_attack'] = time.time()
		else:
			for machine in machines:
				if machine['bot_name'] == bot_name:
					vnc_port = machine['vnc_port']
					qemu_port = machine['qemu_port']
					if time.time() > machine['last_attack'] + 4:
						subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 0.5 -s localhost:{} key f2" - eduardo'.format(vnc_port), shell=True)
						machine['last_attack'] = time.time()
	except Exception as e:
		pass

def checkWings(image, bot_name):
	logging.info('Started the process of checking wings on {}'.format(bot_name))
	img_asa = cv.imread('tests/asa_de_mosca.png',0)
	img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
	w, h = img_asa.shape[::-1]
	res = cv.matchTemplate(img_gray,img_asa,cv.TM_CCOEFF_NORMED)
	threshold = 0.9
	loc = np.where(res >= threshold)
	for pt in zip(*loc[::-1]):
		for machine in machines:
			if machine['bot_name'] == bot_name:
				machine['elapsed_time'] = time.time()
				exit(0)

	#Check if there is another thread alive requesting wings
	for machine in machines:
		if machine['bot_name'] == bot_name:
			if machine['search_thread'].is_alive():
				time.sleep(5)
				exit(0)
		else:
			if machine['wings_thread'].is_alive():
				time.sleep(5)
				exit(0)

	image_name = 'static/{}_{}.jpg'.format(time.strftime("%m-%d-%Y,%H-%M-%S", time.localtime()), bot_name)
	cv.imwrite(image_name, image)
	threading.Thread(target=telegramNotification, args=(image_name,)).start()
	logging.info('Relogin on {}'.format(bot_name))
	script_file('relog', bot_name)
	logging.info('Relogin on Robot.Merchant')
	script_file('relog', 'Robot.Merchant')
	script_file('send_wings', 'Robot.Merchant', request=bot_name)
	logging.info('Sended wings to {}'.format(bot_name))
	time.sleep(5)
	script_file('get_wings', bot_name, 'Robot.Merchant')
	logging.info('Received wings on {}'.format(bot_name))
	time.sleep(5)
	for machine in machines:
		if machine['bot_name'] == bot_name:
			machine['elapsed_time'] = time.time()


def script_file(script_name, bot_name, request = ''):
	for machine in machines:
		if machine['bot_name'] == bot_name:
			vnc_port = machine['vnc_port']
			qemu_port = machine['qemu_port']
			bot_user = machine['bot_user']
			bot_password = machine['bot_password']

	with open('scripts/{}.txt'.format(script_name), 'r') as file:
		file_lines = file.readlines()
		file.close()
	#Parse every line
	for line in file_lines:
		command_type = line.split(' ')
		if command_type[0] == 'wait':
			time.sleep(float(command_type[1]))
		elif command_type[0] == 'sendkey':
			command_string = ' '.join(command_type)[:-1]
			subprocess.call('echo {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(command_string, qemu_port), shell=True)
			time.sleep(0.2)
		elif command_type[0] == 'click':
			click(vnc_port, qemu_port, command_type[1], command_type[2][:-1])
		elif command_type[0] == 'drag':
			drag(vnc_port, qemu_port, command_type[1], command_type[2], command_type[3], command_type[4][:-1])
		elif command_type[0] == 'double_click':
			doubleclick(vnc_port, qemu_port, command_type[1], command_type[2][:-1])
		elif command_type[0]:
			if '{' in command_type[1]:
				if command_type[1][1:-2] == 'bot_user':
					command_string = 'type "{}"'.format(bot_user)
				elif command_type[1][1:-2] == 'bot_password':
					command_string = 'type "{}"'.format(bot_password)
				else:
					command_string = 'type {}'.format(request)
			else:
				command_string = ' '.join(command_type)[:-1]
			normalCommand(vnc_port, qemu_port, command_string)
			

def telegramNotification(image):
	token = open('credentials/telegramToken')
	bot = telegram.Bot(token=token.readline())
	bot.send_photo(chat_id=507188149, photo=open('{}'.format(image), 'rb'))

def checkClick(click_point):    
	#Menu and player infosm with cash shop icon
	if click_point[1] <= 90:
			return 0
	#Map options
	if click_point[1] <= 185 and click_point[1] >= 160:
		if click_point[0] <= 785 and click_point[0] >= 655:
			return 0

	if click_point[0] >= 430:
		click_point[0] = click_point[0] + 10
	if click_point[0] <= 360:
		click_point[0] = click_point[0] - 10

	if click_point[1] >= 345:
			click_point[1] = click_point[1] + 20
	if click_point[1] <= 225:
		click_point[1] = click_point[1] - 20

	if click_point[0] > 0 and click_point[1] > 0:
		return click_point
	
	return 0


def click(vnc_port, qemu_port, x, y):
	result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port , x, y), shell=True)
	while result_code:
		time.sleep(0.5)
		result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port , x, y), shell=True)
	time.sleep(0.1)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port), shell=True)
	time.sleep(0.1)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port), shell=True)

def drag(vnc_port, qemu_port, x_start, y_start, x_end, y_end):
	result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port, x_start, y_start), shell=True)
	time.sleep(0.2)
	while result_code:
		time.sleep(0.5)
		result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port, x_start, y_start), shell=True)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port),shell=True)
	time.sleep(0.2)
	result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port, x_end, y_end),shell=True)
	while result_code:
		time.sleep(0.5)
		result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port, x_end, y_end),shell=True)
	time.sleep(0.2)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port),shell=True)

def normalCommand(vnc_port, qemu_port, command):
	result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} {}" - eduardo'.format(vnc_port, command),shell=True)
	time.sleep(0.2)
	while result_code:
		time.sleep(0.5)
		result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} {}" - eduardo'.format(vnc_port, command),shell=True)

def doubleclick(vnc_port, qemu_port, x, y):
	result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port , x, y), shell=True)
	time.sleep(0.2)
	while result_code:
		time.sleep(0.5)
		result_code = subprocess.call('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 1 -s localhost:{} move {} {}" - eduardo'.format(vnc_port , x, y), shell=True)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port), shell=True)
	time.sleep(0.2)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port), shell=True)
	time.sleep(0.2)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port), shell=True)
	time.sleep(0.2)
	subprocess.call('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port), shell=True)