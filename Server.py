import imagezmq
import threading
import Functions
import time
import sys
from pickle import loads

Functions.last_attack = time.time()
image_hub = imagezmq.ImageHub()
threading.Thread(target=Functions.listenMerchant, args=()).start()

def main():
    socket_port = int(sys.argv[1])
    Functions.machines = loads(Functions.getMachineConfig())
    #Inicializating parameters
    for machine in Functions.machines:
        machine['search_thread'] = threading.Thread()
        machine['wings_thread'] = threading.Thread()
        machine['elapsed_time'] = time.time()
        machine['last_attack'] = time.time()

    image_hub = imagezmq.ImageHub(open_port='tcp://*:{}'.format(socket_port))

    while True:
      
        try:
            machine_name, image = image_hub.recv_image()
            image_hub.send_reply(b'OK')

            for machine in Functions.machines:
                if machine['name'] == machine_name:
                    bot_name = machine['bot_name']
                    if time.time() > machine['elapsed_time'] + 100:
                        #Thread to search for fly wing
                        if machine['wings_thread'].is_alive():
                            pass
                        else:
                            machine['wings_thread'] = threading.Thread(target=Functions.checkWings, args=(image, bot_name))
                            machine['wings_thread'].start()
                    else:
                        #Thread searching for mobs
                        if machine['search_thread'].is_alive():
                            pass
                        else:
                            machine['search_thread'] = threading.Thread(target=Functions.searchDistance, args=(image, bot_name))
                            machine['search_thread'].start()

        except Exception as e:
            print(e)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)