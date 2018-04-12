import datetime
import os
import logging
import random
import urllib.request
import json
import time
import requests

from random import randint, choice

from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement

from flask_restful import Resource, Api

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from threading import Thread
from time import sleep

app = Flask(__name__, static_folder='')
ask = Ask(app, "/")
api = Api(app)
auth = HTTPBasicAuth()

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

## HELPER FUNCTIONS #######################################

def isItAfterNoon():
	# Check to see if its after 12:00 noon. Return bool. 
	minTime = datetime.time(12,0,0)
	now = datetime.datetime.now()
	current = datetime.time(now.hour, now.minute, now.second)
	#print(current, minTime)
	if(current >= minTime):
		return True
	else:
		return False

def getWeather():
	f = urllib.request.urlopen('http://api.wunderground.com/api/[key]/geolookup/conditions/q/[postal_code].json')
	json_string = f.read().decode('utf-8')
	parsed_json = json.loads(json_string)

	location = parsed_json['location']['city'].lower()
	temp_c = parsed_json['current_observation']['temp_c']
	weather = parsed_json['current_observation']['weather'].lower()
	humidity = parsed_json['current_observation']['relative_humidity'].lower()
	feels_like = parsed_json['current_observation']['feelslike_c']

	weather_list = [location, temp_c, weather, humidity,feels_like]

	f.close()
	return weather_list

def makeBaseMoodNum():
	"""This picks a base mood number between 1 (shit) and 10 (amazing) then augments it based on weather"""
	random.seed()
	baseMood = random.randint(1,10)
	print("starting mood: {}".format(baseMood))

	current_weather = getWeather()
	print(current_weather)

	c_temp = current_weather[1]
	c_weather = current_weather[2]
	c_humidity = current_weather[3]

	### Adjust mood base don temperature
	print("temp: {}".format(c_temp))

	if c_temp < 0:
		baseMood -= 1
	elif c_temp > 0 and c_temp < 24:
		baseMood += 2
	elif c_temp > 24 and c_temp < 30:
		baseMood -= 1 
	elif c_temp > 30:
		baseMood -= 2

	print("aftertemp: {}".format(baseMood))

	## Adjust mood based on humidity
	num_humid = int(c_humidity.replace("%",""))
	print("humidity: {} %".format(num_humid))

	if num_humid < 55:
		baseMood += 2 
	elif num_humid > 55:
		baseMood -= 2 

	print("afterhumid: {}".format(baseMood))

	## adulust mood based on observational weather
	print("weather: {}".format(c_weather))

	downers = ["rain","rainy","storm","snow"]
	uppers = ["sunny","overcast","cloudy"]

	if any(w in c_weather for w in downers):
		baseMood -= 1
	elif any(w in c_weather for w in uppers):
		baseMood += 1
	else:
		pass

	print("after weather: {}".format(baseMood))

	return baseMood

def chooseMood():
	""" Choose the final mood based on the final number """
	final_mood = makeBaseMoodNum()
	print("your mood number is: {}".format(final_mood))

	if final_mood < 1:
		return "very upset"
	elif final_mood == 1 or final_mood == 2:
		return "upset"
	elif final_mood == 3 or final_mood == 4:
		return "low"
	elif final_mood == 5 or final_mood == 6:
		return "neutral"
	elif final_mood == 7 or final_mood == 8:
		return "good"
	elif final_mood == 9 or final_mood == 10:
		return "great"
	elif final_mood > 10: 
		return "amazing"
	else:
		return "neutral"

## HUE HELPERS ##############################################

## lights:
## 2 = officelamp
## 4 = bedroom lamp
## 5 = bathroom light

HUE_USER="XXX"	 					## thesis#blender
HUE_ADDR = 'XXX'								 					## hue local address
URL = 'http://{0}/api/{1}/lights/2/state/'.format(HUE_ADDR,HUE_USER)	## whatcha chaning?
hueFlag = False

colors = {
	"green":[0.41,0.51721],
	"red":[0.6679,0.3181],
	"blue":[0.1691,0.0441],
	"light_orange": [0.5201,0.4265],
	"purple": [ 0.3312, 0.1371 ],
	"white": [0.45,0.4]

}

def hueChange(c_values,sat,bri):
	cx = c_values[0]
	cy = c_values[1]
	payload = {"sat":sat,"bri":bri,"xy":[cx,cy]}
	r = requests.put(URL, json.dumps(payload), timeout=5)
	return r

def hueAlert(cmd):
	payload = {"alert":cmd}
	r = requests.put(URL, json.dumps(payload), timeout=5)
	return r

## API ######################################################

@app.route('/')
def index():
	return render_template('main.html')


class AlexaWants(Resource):
	global resource_var
	resource_var = None

	global state
	state = "off"
	
	def __init__(self):
		self.variable = "default" #instance attribute.

	def get(self):
		if(resource_var):
			return {'command': resource_var,'state':state}
		else:
			return {'command': self.variable, 'state':"off"}


api.add_resource(AlexaWants, '/alexawants')

# Function to be called when the timer expires
def resetFunction():
	global state
	global resource_var
	state = "off"
	resource_var = "default"
	print('ran the reset')
	
# Function with the timer
def resetTimer(seconds):
	sleep(seconds)
	resetFunction()

def hueFunction():
	hueChange(colors["blue"],200,200)
	hueAlert("lselect")
	time.sleep(10)
	print("turn it off")
	hueAlert("none")
	hueChange(colors["white"],200,200)
	print(hueFlag)

def hueTimer():
	global hueFlag
	while True:
		if hueFlag:
			hueFunction()
			hueFlag = False
		else:
			time.sleep(1)

## INTENTS ############################################################

@ask.launch
def launch():
	return question("<speak><break time='1s' />Say, do you feel like a smoothie?</speak>").reprompt("Sorry, I didn't get that. Do you want me to make smoothies?")

@ask.intent("BlendIntent")
def blend():
	
	afternoon = isItAfterNoon()
	global resource_var
	global state
	global hueFlag

	## starts the 10 second reset thread the minute it happens
	resetThread = Thread(target=resetTimer, args=(10,)) ## X seconds
	resetThread.start()


	if(afternoon):
		mood = "very upset" #chooseMood()
		print(mood)
		#mood = 5
		print("final mood: {}".format(mood))
		#return question(burp).reprompt("Do you want a smoothie?")
		if mood == "very upset" or mood == "upset":
			## turn on some neo pixels
			#resource_var = "pixels"
			#state = "on"
			hueFlag = True
			hueThread = Thread(target=hueTimer)
			hueThread.start()

			return statement("I'm too sad to make smoothies, maybe I'll just play with this lamp instead.")
		elif mood == "low" or mood == "neutral":
			## play a song
			resource_var = "song"
			state = "on"
			return statement("<speak>I don't feel like a smoothie right now, I think I'd like to meditate for a bit first.<audio src='https://s3.amazonaws.com/soundfxforthings/birds.mp3'/></speak>")
		elif mood == "good" or "great":
			## turn on the blender and make a smothie
			resource_var = "blender"
			state="on"
			return statement("I'm gonna make us smoothies, and its gonna be great!")
		else:
			return statement(mood)
	else:
		return statement("Its too early, come back later.")

@ask.intent('AMAZON.HelpIntent')
def help():
	help_text = render_template('help')
	return question(help_text).reprompt(help_text)

@ask.intent('AMAZON.StopIntent')
def stop():
	bye_text = render_template('bye')
	return statement(bye_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
	bye_text = render_template('bye')
	return statement(bye_text)

@ask.intent('AMAZON.ResumeIntent')
def resume():
	resume_text = render_template('resume')
	return statement(resume_text)

@ask.intent('AMAZON.PauseIntet')
def pause():
	pause_text = render_template('pause')
	return statement(pause_text)

if __name__ == '__main__':
	app.config['ASK_VERIFY_REQUESTS'] = False
	app.run(host="0.0.0.0",port=5004,debug=True, use_reloader=False)	
