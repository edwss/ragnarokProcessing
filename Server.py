import imagezmq
import threading
import Functions
import time
import sys
from pickle import loads

Functions.last_attack = time.time()
image_hub = imagezmq.ImageHub()
merchant_thread = threading.Thread(target=Functions.listenMerchant, args=()).start()

def main():

    socket_port = int(sys.argv[1])
    Functions.machines = loads(Functions.getMachineConfig())
    
    image_hub = imagezmq.ImageHub(open_port='tcp://*:{}'.format(socket_port))

    img = ''

    thread = threading.Thread()
    thread_check = threading.Thread()

    while True:
      
        try:
            machine_name, image = image_hub.recv_image()
            image_hub.send_reply(b'OK')

            for machine in Functions.machines:
                if machine['name'] == machine_name:
                    vnc_port = machine['vnc_port']
                    qemu_port = machine['qemu_port']
                    bot_name = machine['bot_name']
                    try:
                        if machine['elapsed_time']:
                            pass
                    except:
                        machine['elapsed_time'] = time.time()

            if time.time() > machine['elapsed_time'] + 60:
                #Thread to search for fly wing
                if thread_check.is_alive():
                    pass
                else:
                    thread_check = threading.Thread(target=Functions.checkWings, args=(image, bot_name))
                    thread_check.start()
            else:
                #Thread searching for mobs
                if thread.is_alive():
                    pass
                else:
                    thread = threading.Thread(target=Functions.searchMonster, args=(image, vnc_port, qemu_port))
                    thread.start()    


        except Exception as e:
            with open('errors.txt', 'w') as file:
                file.write(str(e))
            file.close()
            pass

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        with open('errors.txt', 'w') as file:
            file.write(str(e))
        file.close()
        pass