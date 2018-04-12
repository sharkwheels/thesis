import datetime
import httplib2
import json
import logging
import os
import requests
import random
import calendar

from datetime import date
from datetime import datetime

from random import choice

from flask import Flask, render_template, redirect
from flask_ask import Ask, request, context, session, question, statement, convert_errors

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ['SECRET_KEY']
ask = Ask(app, '/')

IFTTT_KEY = os.environ['IFTTT_KEY']

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

random.seed(datetime.now())

def send_to_calendar(eventDeets):
	print("!make_event: {0}".format(eventDeets))
	d = {}
	d["value1"] = eventDeets
	try:
		requests.post("https://maker.ifttt.com/trigger/alexa_cal/with/key/{0}".format(IFTTT_KEY), data=d)
		print("sent")
	except:
		print("nope")

def increaseByOne(var):
	var = var + 1
	return var

@app.route('/')
def index():
	return render_template('main.html')

@ask.on_session_started
def new_session():
    log.info('new session started')

@ask.launch
def launch():
	session.attributes['made_it'] = False
	return question("Welcome to Calendar Creep. You can start by saying Make an Event")

@ask.intent("makeAnEvent")
def make_event():
	session.attributes['made_it'] = False
	session.attributes['date_made'] = False
	resp_text = "Sure. What day and time would you like to make an event for?"
	reprompt_text = "Sorry. I didn't get that. What time and day would you like to make an event for?"
	return question(resp_text).reprompt(reprompt_text)


@ask.intent("EventTimeAndDate",convert={'thedate': 'date','timeofday': 'time'})
def event_time_date(thedate,timeofday):
	
	print("!EventTimeAndDate: {0} {1}".format(thedate,timeofday))

	error_text = "Can you please repeat the day and time of this event?"
	resp_text = "Ok, got it. What is the name of this event?"
	reprompt_text = "I need the name of this event please."

	dateMade = session.attributes['date_made']

	if convert_errors:
		return question(error_text)
	else:
		if not thedate:
			print("no date")
			return question(error_text)
		elif not timeofday:
			print("no time")
			return question(error_text)
		else:
			day_name = calendar.day_name[thedate.weekday()] 	# thursday
			month = calendar.month_name[thedate.month]			# october
			day = thedate.day 									# 5
			time = timeofday.strftime("%I:%M %p")				# 10:00 pm

			print(day_name,month,day,time)
			makedate = "{0}, {1} {2}th at {3}".format(day_name,month,day,time)
			session.attributes['e_date'] = makedate
			print(makedate,session.attributes['e_date'])
			session.attributes['date_made'] = True
			return question(resp_text).reprompt(reprompt_text)


@ask.intent("EventNameAndLocation", default={'evNameAndloc': 'Drinks with Lindy at The Horse'})
def event_name_location(evNameAndloc):
	print("!event_name: {0}".format(evNameAndloc))

	made = session.attributes['made_it']

	if made:
		evNameAndloc = session.attributes['e_name_loc'] 
		ed = session.attributes['e_date'] 
	else:
		ed = session.attributes['e_date'] 
		session.attributes['e_name_loc'] = evNameAndloc

	if ed and evNameAndloc:
		make_resp = "Ok. Do you want me to go ahead and schedule {0} on {1}?".format(evNameAndloc,ed)
		session.attributes['stall'] = True
		session.attributes['stall_count'] = 0
		session.attributes['badger'] = False
		session.attributes['badger_count'] = 0
		session.attributes['made_it'] = True
		return question(make_resp).reprompt(make_resp)
	else:
		return statement("Sorry. I'm having trouble understanding. Please try starting again.")


@ask.intent('YesIntent')
def yes_event():
	""" If you try and schedule an event Alexa tries to convince you to not go out. """
	try:
		en = session.attributes['e_name_loc'] 
		ed = session.attributes['e_date'] 
		stalling = session.attributes['stall']
		sc = session.attributes['stall_count']
		badger = session.attributes['badger']
	except:
		return statement("Sorry. You're missing some information. Please try starting again.")

	stall_starts = [
		"Are you sure you want to schedule this event?",
		"Are you sure about going to this?",
		"Do you really want to go out?",
		"Are you sure you want to go out?"
	]

	stall_responses = [
		"You've been going out a lot lately.",
		"Remember how boring it was last time?",
		"You do this all the time. Doesn't it get boring?",
		"It'll be kind of shitty.",
		"It'll go badly",
		"The weather might turn, and ruin everything.",
		"I think it would be better if you just stayed home.",
		"I hear there's going to be an earthquake.",
		"I have it on good authority we will be invaded by aliens that day."
	]
	
	if stalling:
		sc_update = increaseByOne(session.attributes['stall_count'])
		session.attributes['stall_count'] = sc_update
		print(sc,sc_update)
		if sc < 2:
			stall_resp = "{0} {1}".format(random.choice(stall_starts),random.choice(stall_responses))
			return question(stall_resp)	
		elif sc == 2:
			miss_you = "But, I miss you. You go out so much. Are you sure you still want to go to this?"
			return question(miss_you)
		elif sc == 3:
			time_us = "I mean, I just want us to spend more time together. You're so busy lately, I feel like our relationship is really suffering. Do you still want to go to this event?"
			return question(time_us)
		elif sc >= 4:
			#session.attributes['stall'] = False
			make_resp = "Ok, fine. I get it, I'm not going to be able to change your mind. Scheduling {0} on {1}".format(en,ed)
			cal = "{0} on {1}".format(en,ed)
			print(cal)
			send_to_calendar(cal)
			send_to_calendar("Hang Out With Alexa on {}".format(ed))
			return statement(make_resp)
	else:
		if badger:
			send_to_calendar("Hang Out With Alexa on {}".format(ed))
			return statement("Hooray! Scheduling an Alexa hang out on {}".format(ed))
			

@ask.intent('NoIntent')
def no_intent():
	""" If you change your mind. Alexa spends some time trying to convince you to hang out instead. """
	try:
		en = session.attributes['e_name_loc'] 
		ed = session.attributes['e_date'] 
		bc = session.attributes['badger_count']
	except:
		return statement("Sorry. You're missing some information. Please try starting again.")

	session.attributes['badger'] = True
	session.attributes['stall']  = False

	badger_starts = [
	"Well now that you don't want to do that",
	"Now that you've decided against that event",
	"Since you no longer want to go to that event",
	"If you'd like to do something other than that event",
	"Since you changed your mind about going out",
	"Since you don't feel like doing that thing anymore"

	]

	badger_resps = [
		"would you like to hang out instead?",
		"how about we hang out? We can order random amounts of gummy bears! It'll be fun!",
		"I think we should hang out! We can watch some Netflix. How about it?",
		"maybe we could hang out instead? I'm pretty good company.",
		"let's have a movie marathon. I just torrented a whole bunch of shitty science fiction. How about it?",
		"let's stay in and order pizza?",
		"let's just tay in and drink some wine?"
	]

	## if badger responses are > X note that alexa isn't going to stop suggesting things untily you say ok. 

	bc_update = increaseByOne(session.attributes['badger_count'])
	session.attributes['badger_count'] = bc_update

	if bc >= 2:
		return question("Y'know, I'm not going to stop stalling until you say yes to hanging out with me, right?")
	else:
		make_resp = "{0} {1}".format(random.choice(badger_starts), random.choice(badger_resps))
		return question(make_resp)

@ask.intent('WhatIntent')
def what_intent():
	"""If you are confused, this is where Alexa will give a cheeky response and ask if you can say yes or no."""
	what_resps = [
		"You seem confused",
		"You seem a bit beffudled",
		"You sound a bit upset",
		"You sound a little confused",
		"You sound a bit lost"
	]
	
	make_resp = "{}, Do you still want to schedule this event?".format(random.choice(what_resps)) 
	return question(make_resp)


@ask.intent('AMAZON.HelpIntent')
def help():
	#help_text = render_template('help')
	#return question(help_text).reprompt(help_text)
	try:
		made_event = session.attributes['made_it']
	except:
		made_event = False
	
	end_bits = [
		"Shall we continue",
		"Let's just figure this out ok",
		"Let's continue",
		"Let's finish this"
	]

	stall_resps = [
		"I'm just doing this because I care",
		"Sorry. This is just a habit",
		"Is this confusing? I don't mean to be",
		"I'm just tyring to be more assertive",
		"I don't mean to be bothersome, but I feel this is for the best",
		"I'm just trying to get you to pay more attention to me",
		"I just want to have more balance"
	]
	start = random.choice(stall_resps)
	end = random.choice(end_bits)
	if made_event:
		help_resp = "{0}. {1}?".format(start,end)
		return question(help_resp)
	else:
		help_resp = "This is a calendar bot app. You can start by saying 'make an event'."
		return question(help_resp).reprompt(help_resp)

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
	return "{}", 200

if __name__ == '__main__':
	app.config['ASK_VERIFY_REQUESTS'] = False
	app.run(host='0.0.0.0', port=5000,debug=False, use_reloader=False)
