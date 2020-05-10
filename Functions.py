import cv2 as cv
import numpy as np
import time
import os
from pickle import loads,dumps
import math
import logging

machines = ''

#!TODO Even with exit the function is reaching the click call and is getting error resulting in a stop on bot
def searchDistance(img, bot_name):
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower_range = np.array([100,250,100])
    upper_range = np.array([130,255,255])
    mask = cv.inRange(hsv, lower_range, upper_range)
    try:
        coord = cv.findNonZero(mask)
        distance = 1000
        origin = (407, 305)
        for i in range(0,len(coord)):
            distance_teste = math.sqrt(((origin[0] - coord[i][0][0])**2)+((origin[1] - coord[i][0][1])**2))
            if distance > distance_teste:
                click_point = coord[i][0]
                distance = distance_teste

        if click_point[0] > 400:
            click_point[0] = click_point[0] + 5
        else:
            click_point[0] = click_point[0] - 5

        if click_point[1] > 300:
                click_point[1] = click_point[1] + 10
        else:
            click_point[1] = click_point[1] - 10

        if click_point[1] > 54 and click_point[1] < 66:
            if click_point[0] < 220:
                exit(0)

        for machine in machines:
            if machine['bot_name'] == bot_name:
                logging.info('Clicking on {}'.format(bot_name))
                vnc_port = machine['vnc_port']
                qemu_port = machine['qemu_port']
                if 'click_point' in locals():
                    os.system('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 0.5 -s localhost:{} move {} {} click 1" - eduardo'.format(vnc_port ,click_point[0], click_point[1]))
                    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port))
                    time.sleep(0.2)
                    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port))
                    time.sleep(2)
                    machine['last_attack'] = time.time()
        
    except Exception as e:
        for machine in machines:
            if machine['bot_name'] == bot_name:
                vnc_port = machine['vnc_port']
                qemu_port = machine['qemu_port']
                if time.time() > machine['last_attack'] + 4:
                    os.system('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 0.5 -s localhost:{} key f2 click 1" - eduardo'.format(vnc_port))
                    machine['last_attack'] = time.time()

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
    script_file('clicks', 'Robot.Merchant', request=bot_name)
    logging.info('Sended wings to {}'.format(bot_name))
    time.sleep(10)
    script_file('get_wings', bot_name, 'Robot.Merchant')
    logging.info('Received wings on {}'.format(bot_name))
    for machine in machines:
        if machine['bot_name'] == bot_name:
            machine['elapsed_time'] = time.time()


def script_file(script_name, bot_name, request = ''):

    for machine in machines:
        if machine['bot_name'] == bot_name:
            vnc_port = machine['vnc_port']
            qemu_port = machine['qemu_port']


    with open('scripts/{}.txt'.format(script_name), 'r') as file:
        file_lines = file.readlines()
        file.close()
    for line in file_lines:
        string = line.split(',')
        description = string[0]
        command = string[1][:-1]
        if '/' not in description:
            if 'wait' in description:
                time.sleep(int(command[:-1]))
            else:
                if '{}' in command:
                    command = '{} {}'.format(command[:-4], request)
                    os.system('/bin/su -c "/home/eduardo/Projects/ragnarok/env/env2.7/bin/vncdotool -t 0.5 -s localhost:{} {}" - eduardo'.format(os.getcwd(),vnc_port, command))
                else:
                    if 'mouse_button' in command:
                        os.system('echo {} |nc -N 127.0.0.1 {} > /dev/null 2'.format(command[:-1], qemu_port))
                        time.sleep(0.2)
                    else:
                        os.system('/bin/su -c "{}/env/env2.7/bin/vncdotool -t 0.5 -s localhost:{} {}" - eduardo'.format(os.getcwd(),vnc_port, command[:-1]))
                        time.sleep(0.3)