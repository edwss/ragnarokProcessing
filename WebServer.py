# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

from flask import Response
from flask import Flask
from flask import render_template
from flask import request
import threading
import argparse
import datetime
import time
import cv2
import os
# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__,template_folder='templates')
machines = ''
logs = []
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
@app.route("/")
def index():
	logs = getLogs()
	# return the rendered template
	return render_template("index.html",bots=machines)
		
def generate(bot_name):
	# grab global references to the output frame and lock variables
	global lock
	# loop over frames from the output stream
	for machine in machines:
		if machine['bot_name'] == bot_name:
			while True:
				with lock:
					if machine['frame'] is None:
						continue
					try:
						(flag, encodedImage) = cv2.imencode(".jpg", machine['frame'])
					except:
						continue
					if not flag:
						continue
					yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
						bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	bot_name = request.args.get('bot')
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(bot_name),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

def getLogs():
	files_dict = []
	files = os.listdir('static')

	for file_name in files:
		bot_name = file_name.split('_')[1][:-4]
		file_dict = {}
		file_dict['bot_name'] = bot_name
		file_dict['directory'] = file_name
		files_dict.append(file_dict)
	
	return files_dict


# check to see if this is the main thread of execution
def main():
	# start the flask app
	app.run(host='10.0.0.116', port=5000, debug=True,
		threaded=True, use_reloader=False)