import json
import os
import psycopg2
import random
import requests
import time
import urllib.parse

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from random import randint, choice, shuffle
from urllib.parse import urlparse

from flask import Flask, session, render_template
from flask_restful import Resource, Api
from flask_assistant import Assistant, ask, tell, event, context_manager, request
from flask_assistant import ApiAi
from flask_httpauth import HTTPBasicAuth

## so many resposnes
from responses import respGenerator, respDebuging, respTellOff, madResponse,respSwore, respSworeIrate
from responses import respHelp, mockResp, newsResp, hey_you, weatherResp, weatherDiss, issueResp, howLongResp, lampResp, lampFollowUp, meanResp, lyingResp

### APP SETTINGS ################################################################

app = Flask(__name__)
print(app)
assist = Assistant(app)
api = Api(app)
auth = HTTPBasicAuth()

CSRF_ENABLED = True
SECRET_KEY = os.environ['SECRET_KEY']		## Config
HUE_KEY = os.environ['HUE_KEY']				## IFTTT
USER_NAME = os.environ['USER_NAME']			## Admin / Monitor
USER_PASS = os.environ['USER_PASS']			## admin / Monitor
DATABASE_URL = os.environ['DATABASE_URL']	## Postgres
DEVELOPMENT = True 							## Dev
DEBUG = True 								## set the debug
USE_RELOADER = False						## set the reolader
USER_DATA = {USER_NAME: USER_PASS}			## monitor login

HUE_USER = os.environ['HUE_USER']			## hue user
HUE_ADDR = 'XXX'						## hue local address
#URL = 'http://{0}/api/{1}/groups/0/action/'.format(HUE_ADDR,HUE_USER)	## whatcha chaning?
URL = 'http://{0}/api/{1}/lights/2/state/'.format(HUE_ADDR,HUE_USER)

## lights:
## 2 = officelamp
## 4 = bedroom lamp
## 5 = bathroom light

### DATABASE CONNECTION ################################################################

conn = None
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(DATABASE_URL)
random.seed(datetime.now())

try:
	conn = psycopg2.connect(
		database=url.path[1:],
		user=url.username,
		password=url.password,
		host=url.hostname,
		port=url.port
	)
	print(conn)
	cur = conn.cursor()
except psycopg2.Error as e:
	if conn:
		conn.rollback()
	print("DB ERROR: {}".format(e))

def fetchValues():
	try:
		cur.execute("SELECT * FROM feels")
		rows = cur.fetchall()
		return rows
	except psycopg2.Error as e:
		print("psycog2 error".format(e))
		## put some logging in here 

def insertValues(values):
	try:
		print("!insertValues: {}".format(values))
		query = """ UPDATE feels
					SET interrupt_count = %s, 
						frustration_count = %s,
						help_count = %s,
						swear_count = %s,
						weather_count = %s,
						news_count = %s,
						lamp_count = %s
					WHERE id = %s"""
		cur.execute(query, (values["ic"],values["fc"],values["hc"],values["sc"], values["wc"], values["nc"], values["lc"], values["user"]))
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as e:
		print("DB ERROR inserting: {}".format(e))

### HELPER FUNCTIONS ################################################################

def makeValues():
	try:
		v = fetchValues()
		print("!makeValues: {}".format(v))
		if v:
			us = v[0][0]
			ic = v[0][1]
			fc = v[0][2]
			hc = v[0][3]
			sc = v[0][4]
			wc = v[0][5]
			nc = v[0][6]
			lc = v[0][7]
			values = {"user":us,"ic":ic,"fc": fc, "hc": hc, "sc":sc, "wc":wc, "nc":nc, "lc":lc}
			return values
		else:
			## give it a fallback / default
			values = {"user":1,"ic":1,"fc": 1, "hc": 1, "sc":1, "wc":wc, "nc":nc, "lc":lc}
	except:
		print("there was an issue pulling the values from the db")

def increaseByOne(var):
	var = var + 1
	return var

def resetValues(values):
	v = values
	v["ic"] = 0	# interrupt count
	v["fc"] = 0	# frustration count
	v["hc"] = 0	# help 
	v["sc"] = 0	# swear
	v["wc"] = 0	# weather
	v["nc"] = 0	# news 
	v["lc"] = 0	# lamp
	print(v)
	try:
		insertValues(v)
	except:
		pass

	print("!resetValues: {}".format(values))


######## HUE #####################################################################

def hueChange(c_values,sat,bri):
	cx = c_values[0]
	cy = c_values[1]
	payload = {"sat":sat,"bri":bri,"xy":[cx,cy]}
	r = requests.put(URL, json.dumps(payload), timeout=5)
	return r

def hueOnOff(cmd):
	payload = {"on":cmd}
	r = requests.put(URL, json.dumps(payload), timeout=5)
	return r

def hueAlert(cmd):
	payload = {"alert":cmd}
	r = requests.put(URL, json.dumps(payload), timeout=5)
	return r

def hueBrightness(bri):
	payload = {"bri":bri}
	r = requests.put(URL, json.dumps(payload), timeout=5)
	return r

def hueFade(c_values,bri,trans):
	cx = c_values[0]
	cy = c_values[1]
	payload = {"bri":bri,"sat":25,"transitiontime":trans,"xy":[cx,cy]}
	r = requests.put(URL, json.dumps(payload), timeout=5)
	return r

colors = {
	"green":[0.41,0.51721],
	"red":[0.6679,0.3181],
	"blue":[0.1691,0.0441],
	"light_orange": [0.600,0.4365], #[0.5201,0.4265],
	"purple": [ 0.3312, 0.1371 ],
	"white": [0.45,0.4]


}

flags = {"breatheFlag": False}
lampStates = {"breatheState":0}


def slowBreathe(color1,bri1,trans1, color2,bri2,trans2):
	startFlag = flags["breatheFlag"]
	if startFlag:
		breatheState = lampStates["breatheState"]
		#print("slowBreathe: breatheState {0}".format(breatheState))
		if breatheState == 0:
			hueFade(color1,bri1,trans1)
			lampStates.update({'breatheState': 1})
		else:
			hueFade(color2,bri2,trans2)
			lampStates.update({'breatheState': 0})
	else:
		time.sleep(1)


sched = BackgroundScheduler()
sched.add_job(slowBreathe, "interval", [colors["red"],2,10, colors["red"],200,10],seconds=3)
sched.start()

 
######## VIEWS #####################################################################

### just makes sure everything is REALLY zero if the quit function crapped out. 
## might not be best solution. but for now is ok.
@app.before_first_request
def hardReset():
	v = makeValues()
	print("!beforeFirstReq: {}".format(v))
	resetValues(v)
	hueOnOff(False)
	flags.update({'breatheFlag': False})


### GOOGLE ASSISTANT ##########################################################

@assist.action('greeting')
def hello_world():
	hueOnOff(True)
	hueChange(colors["white"], 200, 200)
	flags.update({'breatheFlag': False})
	speech = 'Hello, welcome to home hub. You can do things like control the temperature, play some music, or ask me about traffic. What would you like to do?'
	print("!greetings".format(speech))
	return ask(speech)

@assist.context("greeting-followup")
@assist.action('greeting-custom')
def greet_custom():
	hueChange(colors["red"], 200, 200)
	flags.update({'breatheFlag': False})
	issue = issueResp()
	return ask(issue)


@assist.action('fallback', is_fallback=True)
def say_fallback():
	v = makeValues()
	default_resp = "uggggggh what do you wannnnnt?"
	user_said = request['result']['resolvedQuery']
	print("!say_fallback: {}".format(user_said))
	# might want to wrap this in a try / except block
	if user_said:
		# if frustration is 3, rage quit
		if v["fc"] == 3:
			flags.update({'breatheFlag': False})
			hueOnOff(False)	#turn off			
			resp = madResponse()				
			resetValues(v)						
			return tell(resp)					
		else:
			hueChange(colors["red"], 200, 200)
			flags.update({'breatheFlag': True})
			resp = respDebuging()
			interrupt_count = increaseByOne(v["ic"])
			v["ic"] = interrupt_count
			try:
				insertValues(v)
			except:
				pass
			print(interrupt_count)
			if not interrupt_count % 3:	
				frustration_count = increaseByOne(v["fc"])
				v["fc"] = frustration_count
				try:
					insertValues(v)
				except:
					pass
				resp = respTellOff()		
			elif not interrupt_count % 7:	
				resp = "blah blah blah {0}, blah.".format(user_said)	
				print(resp)
			elif not interrupt_count % 5:
				resp = hey_you()
				print(resp)
			return ask(resp)
	else:
		print(default_resp)
		return(default_resp)

@assist.action('how-long-will-this-take')
def how_long():
	flags.update({'breatheFlag': False})
	hueChange(colors["green"], 200, 200)
	v = makeValues()
	interrupt_count = v["ic"]
	resp = howLongResp(interrupt_count)
	return ask(resp)


@assist.action('help')
def help():
	hueChange(colors["green"], 200, 200)
	flags.update({'breatheFlag': False})
	v = makeValues()
	if v:
		help_count = increaseByOne(v["hc"])
		v["hc"] = help_count
	## change the help response based on the level of frustration. 
	speech = "This is the help section"
	if v["hc"] == 0:
		speech = "I found an issue, so I'm currently trying to debug myself."
	elif v["hc"] == 1:
		speech = "Sorry, something glitched out and I am trying to debug it."
	elif v["hc"] == 2:
		speech = "I'm sorry, I really have to do this debugging. Its important."
	elif v["hc"] == 3:
		speech = "Oh my god. Just go away and let me finish this debugging."
	elif v["hc"] > 3:
		speech = respHelp()
	insertValues(v)
	print(speech)
	return ask(speech)

@assist.action('swearing')
def swear_response():
	flags.update({'breatheFlag': False})
	## make a fast on/off toggle function for flickering.
	hueChange(colors["blue"], 200, 200)
	v = makeValues()
	sc_update = increaseByOne(v["sc"])
	v["sc"] = sc_update
	insertValues(v)
	if v["sc"] >= 0 and v["sc"] <= 2:
		speech = respSwore()			## asking for an apology
	elif v["sc"] > 2:
		speech = respSworeIrate()		## being irate back at you
	print(speech)
	return ask(speech)


@assist.action('weather')
def weather_response():
	hueChange(colors["light_orange"], 200, 200)
	flags.update({'breatheFlag': False})
	v = makeValues()
	wc_update = increaseByOne(v["wc"])
	v["wc"] = wc_update
	insertValues(v)
	w = weatherResp()
	wF = [
		"So you're looking for the weather eh? Well its going to",
		"Want to know the weather huh? Looks like its going to",
		"Current weather reports say it most likely to"
	]
	speech = "{} {} ".format(random.choice(wF),w)
	return ask(speech)

@assist.context("weather-followup")
@assist.action('weather-diss')
def weather_diss():
	flags.update({'breatheFlag': False})
	speech = weatherDiss()
	return ask(speech)

@assist.action('news')
def news_response():
	hueChange(colors["light_orange"], 200, 200)
	flags.update({'breatheFlag': False})
	v = makeValues()
	nc_update = increaseByOne(v["nc"])
	v["nc"] = nc_update
	insertValues(v)
	news = newsResp()
	return ask(news)


@assist.action('lamp')
def lamp_resp():
	flags.update({'breatheFlag': False})
	hueChange(colors["light_orange"], 200, 200)
	v = makeValues()
	lc_update = increaseByOne(v["lc"])
	v["lc"] = lc_update
	insertValues(v)
	speech = lampResp()
	return ask(speech)

@assist.context("lamp-followup")
@assist.action('lamp-custom')
def lamp_custom():
	flags.update({'breatheFlag': False})
	speech = lampFollowUp()
	return ask(speech)

@assist.action("lying")
def yer_lying():
	flags.update({'breatheFlag': False})
	speech = lyingResp()
	return ask(speech)

@assist.action("youre-mean")
def yer_mean():
	speech = meanResp()
	return ask(speech)


@assist.action('quit')
def quit():
	hueChange(colors["white"], 200, 200)
	flags.update({'breatheFlag': False})	
	v = makeValues()
	resetValues(v)
	speech = "Leaving program and resetting everything."
	return tell(speech)

### APP VIEWS ################################################################

@auth.verify_password
def verify(username, password):
	if not (username and password):
		return False
	return USER_DATA.get(username) == password

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/reset')
@auth.login_required
def reset():
	hueChange(colors["white"], 200, 200)
	v = resetValues()
	resetValues(v)
	return "reseting values"

@app.route('/monitoring')
@auth.login_required
def monitor():
	v = makeValues()
	print("!mointoring: ".format(v))
	return render_template('monitor.html',interruption=v["ic"], frustration=v["fc"], help=v["hc"], swears=v["sc"], weather=v["wc"], news=v["nc"], lamp=v["lc"])

### API REST THING ################################################################

class GF(Resource):
	@auth.login_required # might have to take it out?
	def get(self):
		v = makeValues()
		print(v)
		GOOGLE_FEELS = {
			'feel1': {'interruption': v["ic"]},
			'feel2': {'frustration': v["fc"]},
			'feel3': {'help': v["hc"]},
			'feel4': {'swears': v["sc"]},
			'feel5': {'weather': v["wc"]},
			'feel6': {'news': v["nc"]},
			'feel7': {'lamp': v["lc"]}
		}
		return GOOGLE_FEELS

api.add_resource(GF, '/googlefeels')

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5003, debug=True, use_reloader=False)
