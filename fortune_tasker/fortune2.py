import calendar
import datetime
import json
import logging
import os
import requests
import random
import time

from random import choice
from datetime import date
from data import holidays, verbs, objects, dates, locations, tasks, absurds, nicknames

from flask import Flask, render_template, redirect
from flask_ask import Ask, request, context, session, question, statement, convert_errors
from flask_restful import Resource, Api

app = Flask(__name__,static_folder='static',static_url_path='/static')
app.secret_key = "XXXX"

ask = Ask(app, '/')
api = Api(app)

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

## random seed this thing
random.seed(datetime.datetime.now())

## Is this hackey or is this just a database? Whooooo knowwwwssss.
jsonResps = {"resp1": "", 
			"resp2":"",
			"resp3": "",
			"resp4":"", 
			"timestamp": "",
			"greeting":""
			}

def timeStamp():
	today = datetime.date.today()					
	day_name = calendar.day_name[today.weekday()]	# thursday
	month = calendar.month_name[today.month]		# october
	day = today.day 								# 5
	t = time.strftime("%-I:%M %p")					# 4:10 PM
	current_time = "{0} {1} {2}th, {3}".format(day_name,month,day,t)
	return current_time

def findHoliday():
	""" Get the current date, and then do a serch through the dict for a holiday that matches it """
	today = datetime.date.today()
	month = calendar.month_name[today.month]
	day = today.day 
	current_time = "{0} {1}".format(month,day)
	print(current_time)

	## append holidays to hols
	hols = []
	for d in holidays:
		if d["day"] == current_time:
			h = d['holiday']
			hols.append(h)
	
	## sometimes there are two entries for a day
	if len(hols) > 0:
		boop = random.choice(hols)
		return boop
	else:
		return "Royal Spaggetti Day"


def makeFortune():
	"""
	Hello [NICKNAMES], happy [HOLIDAY]
	You will [VERB] [OBJECT] [DATE],
	I foresee you will [VERB] [OBJECT]. 
	Watch out for [OBJECT][LOCATION]. 
	Your task is [TASK].
	"""
	## greeting
	holiday = findHoliday()
	nick = random.choice(nicknames)

	## first scentance
	verb1 = random.choice(verbs)
	object1 = random.choice(objects)
	date = random.choice(dates)

	## second scentence
	verb2 = random.choice(verbs)
	object2 = random.choice(objects)

	## third scentence
	object3 = random.choice(objects)
	location = random.choice(locations)

	## fourth scentance
	task = random.choice(tasks)


	## gonna have to split this up in the JSON because is fucking looooooong
	greeting = "Hello {0}, happy {1}! Your future is as follows:".format(nick,holiday)
	fortunePt1 = "You will {0} {1} {2}.".format(verb1,object1,date)
	foruntePt2 = "I foresee you will {0} {1}.".format(verb2,object2)
	fortunePt3 = "Watch out for {0} {1}.".format(object3,location)
	fortunePt4 = "Your task is: {0}.".format(task)
	
	fortune_list = [greeting,fortunePt1,foruntePt2, fortunePt3,fortunePt4]
	print(fortune_list)
	return fortune_list

def reset():
	jsonResps["greeting"] = ""
	jsonResps["resp1"] = ""
	jsonResps["resp2"] = ""
	jsonResps["resp3"] = ""
	jsonResps["resp4"] = ""

def makeTheResponse():
	## make all the rando statements to return
	make_resp = makeFortune()
	ts = timeStamp()
	## greeting, fortunePt1, fortunePt2, fortunePt3, fortunePt4 
	this_resp = "{0} {1} {2} {3} {4}".format(make_resp[0],make_resp[1],make_resp[2],make_resp[3], make_resp[4])

	## set the JSON so the printer can grab / parse it
	jsonResps["timestamp"] = ts
	jsonResps["greeting"] = make_resp[0]
	jsonResps["resp1"] = make_resp[1]
	jsonResps["resp2"] = make_resp[2]
	jsonResps["resp3"] = make_resp[3]
	jsonResps["resp4"] = make_resp[4]

	return this_resp


### APP VIEWS AND RESOURCES ######################

@app.route('/',methods=['GET','POST'])
def index():
	return render_template('main.html')


class AlexaSays(Resource):
	def get(self):
		return {'msg1': jsonResps["resp1"],
				'msg2': jsonResps["resp2"],
				'msg3': jsonResps["resp3"],
				'msg4': jsonResps["resp4"],
				'timestamp' : jsonResps["timestamp"],
				'greeting': jsonResps["greeting"]
				}

api.add_resource(AlexaSays, '/alexasays')


### ALEXA TTHINGS #####################

@ask.on_session_started
def new_session():
	log.info('new session started')
	log.info(request.locale)
	beep = request.locale
	print(beep)

@ask.launch
def launch():
	""" Get and return the fortune """
	to_speak = makeTheResponse()
	return statement("<speak>{0}<break time='1s' /></speak>".format(to_speak)) ## 5 second break after resp, should extend timeout


@ask.intent("FutureIntent")
def future_intent():
	""" Get and return the fortune (this is so crass) """
	to_speak = makeTheResponse()
	return statement("<speak>{0}<break time='1s' /></speak>".format(this_resp)) ## 3 second break after resp, should extend timeout


@ask.intent('AMAZON.HelpIntent')
def help():
	help_text = render_template('help')
	return question(help_text).reprompt(help_text)

@ask.intent('AMAZON.StopIntent')
def stop():
	bye_text = render_template('stop')
	return statement(bye_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
	bye_text = render_template('cancel')
	return statement(bye_text)

@ask.session_ended
def session_ended():
	log.debug("Session Ended")
	print("session ended")
	reset()
	return "{}", 200

if __name__ == '__main__':
	app.config['ASK_VERIFY_REQUESTS'] = False
	app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
