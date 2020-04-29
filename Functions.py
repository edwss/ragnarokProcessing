import pika
import cv2 as cv
import numpy as np
import time
import os
from pickle import loads,dumps
import math

last_attack = time.time()
machines = ''

def searchMonster(img, vnc_port, qemu_port):
    global last_attack
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower_range = np.array([100,250,100])
    upper_range = np.array([130,255,255])
    mask = cv.inRange(hsv, lower_range, upper_range)
    try:
        coord = cv.findNonZero(mask)
        x, y = coord[50][0]
    except:
        if time.time() > last_attack + 6:
            os.system('env/env_python2.7/bin/vncdotool -s localhost:{} key f2 click 1'.format(vnc_port))
            last_attack = time.time()
        return
    os.system('env/env_python2.7/bin/vncdotool -s localhost:{} move {} {} click 1'.format(vnc_port ,x, y))
    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port))
    time.sleep(0.2)
    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port))
    time.sleep(3.5)
    last_attack = time.time()

def searchDistance(img, vnc_port, qemu_port):
    global last_attack
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower_range = np.array([100,250,100])
    upper_range = np.array([130,255,255])
    mask = cv.inRange(hsv, lower_range, upper_range)
    try:
        coord = cv.findNonZero(mask)
        distance = 1000
        origin = (407, 305)
        for pixel in coord:
            x,y = pixel[0]
            distance_teste = math.sqrt(((origin[0]-x)**2)+((origin[1]-y)**2))
            if distance > distance_teste:
                click_point = (x,y)
                distance = distance_teste
    except:
        if time.time() > last_attack + 6:
            os.system('env/env_python2.7/bin/vncdotool -s localhost:{} key f2 click 1'.format(vnc_port))
            last_attack = time.time()
        return
    os.system('env/env_python2.7/bin/vncdotool -s localhost:{} move {} {} click 1'.format(vnc_port ,click_point[0], click_point[1]))
    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port))
    time.sleep(0.2)
    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port))
    time.sleep(3)
    last_attack = time.time()


def getMachineConfig():
    credentials = pika.PlainCredentials('eduardo', 'edu12309')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.0.0.112',credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='Machines')
    method_frame, header_frame, body = channel.basic_get(queue = 'Machines')          
    # channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    connection.close() 
    return body

def getMerchantChannel():
    try:
        credentials = pika.PlainCredentials('eduardo', 'edu12309')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.0.0.112',credentials=credentials))
        channel = connection.channel()

        channel.queue_declare(queue='Merchant')
        method_frame, header_frame, body = channel.basic_get(queue = 'Merchant')          
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close() 
    except:
        return ''
    return body

def setMerchantChannel(bot_name):
    credentials = pika.PlainCredentials('eduardo', 'edu12309')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.0.0.112', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='Merchant')
    channel.basic_publish(exchange='',routing_key='Merchant',body=bot_name)
    connection.close()

def checkWings(image, bot_name):
    img_asa = cv.imread('tests/asa_de_mosca.png',0)
    img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    w, h = img_asa.shape[::-1]
    res = cv.matchTemplate(img_gray,img_asa,cv.TM_CCOEFF_NORMED)
    threshold = 0.6
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        for machine in machines:
            if machine['bot_name'] == bot_name:
                machine['elapsed_time'] = time.time()
        return 1
    cv.imwrite('logs/{}_{}.jpg'.format(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()), bot_name), image)
    setMerchantChannel(bot_name)
    time.sleep(90)
    script_file('get_wings', bot_name, 'Robot.Merchant')
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
                    os.system('env/env_python2.7/bin/vncdotool -s localhost:{} {}'.format(vnc_port, command))
                else:
                    if 'mouse_button' in command:
                        os.system('echo {} |nc -N 127.0.0.1 {} > /dev/null 2'.format(command[:-1], qemu_port))
                        time.sleep(0.2)
                    else:
                        os.system('env/env_python2.7/bin/vncdotool -s localhost:{} {}'.format(vnc_port, command[:-1]))
                        time.sleep(0.3)


def listenMerchant():
    while True:
        result = getMerchantChannel()
        if result !=  '':
            script_file('clicks', 'Robot.Merchant', request=result.decode('utf-8'))
        time.sleep(20)