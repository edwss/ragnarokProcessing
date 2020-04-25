import cv2 as cv
import imagezmq
import threading
import numpy as np
import os
import time
import sys
from pickle import loads
import pika

last_attack = time.time()

def background_search(img, vnc_port, qemu_port):
    global last_attack
    global last_check
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

def getMachineConfig():
    credentials = pika.PlainCredentials('eduardo', 'edu12309')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.0.0.112',credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='Machines')
    method_frame, header_frame, body = channel.basic_get(queue = 'Machines')          
    # channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    connection.close() 
    return body

image_hub = imagezmq.ImageHub()

def main():

    socket_port = int(sys.argv[1])
    machines = loads(getMachineConfig())
    
    image_hub = imagezmq.ImageHub(open_port='tcp://*:{}'.format(socket_port))

    img = ''

    thread = threading.Thread()

    while True:
        try:
            machine_name, image = image_hub.recv_image()
            #cv.imshow(machine_name, image)
            #cv.waitKey(1)
            image_hub.send_reply(b'OK')

            for machine in machines:
                if machine['name'] == machine_name:
                    vnc_port = machine['vnc_port']
                    qemu_port = machine['qemu_port']

            if thread.is_alive():
                    pass
            else:
                # print('Started again')
                thread = threading.Thread(target=background_search, args=(image,vnc_port, qemu_port))
                thread.start()
        except Exception as e:
            with open('errors.txt', 'w') as file:
                file.write(e + '\n')
            file.close()
            pass

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        with open('errors.txt', 'w') as file:
            file.write(e + '\n')
        file.close()
        pass

#!TODO Verificar se o bot esta sem asa de mosca, e se estiver publicar no canal do Merchant
#!TODO Veriricar o canal do Merchant e mandar a asa de mosca com ack
#!TODO Pegar as asas de mosca no RODEX
#!TODO Enviar os morangos para o Merchant