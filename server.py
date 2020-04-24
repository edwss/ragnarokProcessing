import cv2 as cv
import imagezmq
import threading
import numpy as np
import os
import time
import sys

last_attack = time.time()

def background_search(img, vnc_port, qemu_port):
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
            os.system('env/bin/vncdotool -s localhost:{} key f2 click 1'.format(vnc_port))
            last_attack = time.time()
        return
    os.system('env/bin/vncdotool -s localhost:{} move {} {} click 1'.format(vnc_port ,x, y))
    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(1, qemu_port))
    time.sleep(0.2)
    os.system('echo mouse_button {}|nc -N 127.0.0.1 {} > /dev/null 2'.format(0, qemu_port))
    time.sleep(3.5)
    last_attack = time.time()


image_hub = imagezmq.ImageHub()

def main():

    socket_port = int(sys.argv[1])
    vnc_port = sys.argv[2]
    qemu_port = sys.argv[3]

    print('Started Running')
    image_hub = imagezmq.ImageHub(open_port='tcp://*:{}'.format(socket_port))

    img = ''

    thread = threading.Thread(target=background_search, args=(img,vnc_port, qemu_port))
    thread.start()

    while True:
        machine_name, image = image_hub.recv_image()
        cv.imshow(machine_name, image)
        cv.waitKey(1)
        image_hub.send_reply(b'OK')
        if thread.is_alive():
                pass
        else:
            print('Started again')
            thread = threading.Thread(target=background_search, args=(image,vnc_port, qemu_port))
            thread.start()

if __name__ == '__main__':
    main()