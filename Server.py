import threading
import Functions
import time
import sys
import imagezmq
from pickle import loads
import logging

logging.basicConfig(level=logging.INFO)
image_hub = imagezmq.ImageHub()
socket_port = ''

def main():
	for machine in Functions.machines:
		machine['search_thread'] = threading.Thread()
		machine['wings_thread'] = threading.Thread()
		machine['elapsed_time'] = time.time()
		machine['last_attack'] = time.time()
		machine['frame'] = ''

	image_hub = imagezmq.ImageHub(open_port='tcp://*:{}'.format(socket_port))
	while True:
		try:
			machine_name, image = image_hub.recv_image()
			image_hub.send_reply(b'OK')
			for machine in Functions.machines:
				if machine['name'] == machine_name:
					bot_name = machine['bot_name']
					machine['frame'] = image
					if time.time() > machine['elapsed_time'] + 360:
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
			logging.warning(e)