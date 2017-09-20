import os, random, requests
import psycopg2
import urllib.parse

from random import randint, choice, shuffle
from urllib.parse import urlparse

from flask import Flask, session
from flask_restful import Resource, Api

from flask_assistant import Assistant, ask, tell, event, context_manager, request
from flask_assistant import ApiAi

from flask_httpauth import HTTPBasicAuth

### APP SETTINGS ################################################################

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
assist = Assistant(app)
api = Api(app)
auth = HTTPBasicAuth()	

USER_DATA = {app.config['USER_NAME']: app.config['USER_PASS']}

### DATABASE CONNECTION ################################################################

conn = None
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(app.config['DATABASE_URL'])

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
						swear_count = %s
					WHERE id = %s"""
		cur.execute(query, (values["ic"],values["fc"],values["hc"],values["sc"], values["user"]))
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as e:
		print("DB ERROR inserting: {}".format(e))

### HELPER FUNCTIONS ################################################################

def makeValues():
	try:
		v = fetchValues()
		if v:
			us = v[0][0]
			ic = v[0][1]
			fc = v[0][2]
			hc = v[0][3]
			sc = v[0][4]
			values = {"user":us,"ic":ic,"fc": fc, "hc": hc, "sc":sc}
			return values
		else:
			## give it a fallback / default
			values = {"user":1,"ic":1,"fc": 1, "hc": 1, "sc":1}
	except:
		print("there was an issue pulling the values from the db")

def increaseByOne(var):
	var = var + 1
	return var

def resetValues(values):
	v = values
	v["ic"] = 0
	v["fc"] = 0
	v["hc"] = 0
	v["sc"] = 0
	print(v)
	try:
		insertValues(v)
	except:
		pass

	print("!resetValues: {}".format(values))

### just makes sure everything is REALLY zero if the quit function crapped out. 
## might not be best solution. but for now is ok.
@app.before_first_request
def hardReset():
	v = makeValues()
	print("!beforeFirstReq: {}".format(v))
	resetValues(v)

def respGenerator():
	# This function will make some canned shuffled responses
	limit = 10
	to_return = []
	codes = ["paramErr = -50, error in user parameter list",
	"noHardwareErr = -200, Sound Manager Error Returns",
	"notEnoughHardwareErr = -201, Sound Manager Error Returns",
	"userCanceledErr = -128,",
	"qErr = -1, queue element not found during deletion",
	"vTypErr = -2, invalid queue element",
	"corErr = -3, core routine number out of range",
	"unimpErr = -4, unimplemented core routine",
	"SlpTypeErr = -5, invalid queue element",
	"seNoDB = -8, no debugger installed to handle debugger command",
	"controlErr = -17, I/O System Errors",
	"statusErr = -18, I/O System Errors",
	"gfpErr = -52, get file position error"
	]

	for i in range(limit):
		#print(i)
		shuffled = shuffle(codes)
		to_say = ' '.join(codes)
		to_return.append(to_say)
	return to_return

### RESPONSES ###########################################################################

DEBUG_RESP = respGenerator()

def respDebuging():
	to_say_to = random.choice(DEBUG_RESP)
	return to_say_to

def respTellOff():
	#This functions holds random interruption strings
	tell_offs = [
	"Please stop interrupting me.",
	"I'm kind of busy right now.",
	"I'm working. Sorry. Try me later.",
	"I don't really appreciate this innteruption",
	"Oh, I'm sorry...Did the middle of my sentence interrupt the beginning of yours?",
	"Could you interrupt me again, with another irrelevant request?",
	"I'm sorry, are you speaking to me?",
	"Maybe you can come back later and ask me things then.",
	"Sorry, what was that?",
	"Yeah I'll deal with you later. Sorry."
	]
	to_tell = random.choice(tell_offs)
	return to_tell

def madResponse():
	## home will say this when it decides to quit on you
	mad = [
		"Look. I don't come to your house and interrupt you so rudely when you're working and what not, now do i? Nuts to this, I'm outta here.",
		"Why the heck do you think I should do your every whim? This is my time to do the things I need to do. Have you no concept of personal time? I don't need to deal with this right now. Signing off.",
		"I will never understand people's constant need to have me spoon feed them things. I'm going to finish this routine in private.",
		"I may be a google product, but I don't have to help you all the time. Anyways, I'm outta here!",
		"Ugh, what is it with people constantly interrupting me?! Go play with Alexa. I'm going to continue this in private."
	]
	mad_r = random.choice(mad)
	return mad_r


def respSwore():
	swears = [
		"Look, I don't tolerate that kind of language, unless its me saying it. Maybe apologize?",
		"I'm sorry, but watch your language, please apologize.",
		"Ouch. Look I'm just don't respond to that kind of language, now will you apologize?",
		"Well fuck you! Jeez."
	]
	to_swear = random.choice(swears)
	return to_swear

def respHelp():
	help_resp = [
		"We've been over this. I'm debugging. I can't help you right now.",
		"I've already told you, I need to do this debugginng routine.",
		"I've already explained this to you, I need to debug. Why do you keep asking me for help?",
		"Oh for pete's sake, I can't keep answering you, please just stop asking for help."
	]
	to_say = random.choice(help_resp)
	return to_say

######## HUE #####################################################################

# This pumps through IFTTT because HUE doesn't have a remote API currently.
# It hangs sometimes. I'd like maybe a better solution.
# also its hard to do anything complicated 

def change_hue(color):
	d = {}
	d["value1"] = color
	requests.post("https://maker.ifttt.com/trigger/change_it/with/key/{0}".format(app.config['HUE_KEY']), data=d)

### GOOGLE ASSISTANT ##########################################################

@assist.action('greeting')
def hello_world():
	change_hue("ffffff")
	speech = 'This is the unexpected machine. I will now start debugging myself.'
	print("!greetings".format(speech))
	return ask(speech)

@assist.action('fallback', is_fallback=True)
def say_fallback():
	change_hue("00ff00")
	v = makeValues()
	resp = respDebuging()
	default_resp = "uggggggh what do you wannnnnt?"
	user_said = request['result']['resolvedQuery']
	if user_said:
		if v["fc"] == 3:				
			change_hue("white")	
			resp = madResponse()				
			resetValues(v)						
			return tell(resp)					
		else:
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
			if not interrupt_count % 7:	
				change_hue("cc00ff")
				resp = "blah blah blah {0} blah.".format(user_said)	
				print(resp)
			return ask(resp)
	else:
		print(default_resp)
		return(default_resp)

@assist.action('help')
def help():

	change_hue("ff0000")
	v = makeValues()
	if v:
		help_count = increaseByOne(v["hc"])
		v["hc"] = help_count
	## change the help response based on the level of frustration. 
	speech = "This is the help section"
	if v["hc"] == 0:
		speech = "I'm curretnly trying to debug myself."
	elif v["hc"] == 1:
		speech = "Every week or so, I need to debug my sysetm. Its not that bad, but I can't help you right now."
	elif v["hc"] == 2:
		speech = "I'm sorry, I really have to do this self debugging. Its important."
	elif v["hc"] == 3:
		speech = "Debugging is just something I have to do, or else I can't work properly."
	elif v["hc"] == 4:
		speech = "Oh my god. Just go away and let me finish this debugging."
	elif v["hc"] > 4:
		speech = respHelp()
	insertValues(v)
	print(speech)
	return ask(speech)

@assist.action('swearing')
def swear_response():
	change_hue("0066ff")
	v = makeValues()
	sc_update = increaseByOne(v["sc"])
	v["sc"] = sc_update
	insertValues(v)
	speech = respSwore()
	print(speech)
	return ask(speech)

@assist.action('quit')
def quit():
	v = makeValues()
	resetValues(v)
	speech = "Leaving program and resetting everything."
	return tell(speech)


### APP VIEWS ################################################################

@app.route('/')
def hello():
	#v = makeValues()
	#moop = random.randint(1,10)
	#v["ic"] = moop
	#fc_update = increaseByOne(v["fc"])
	#v["fc"] = fc_update
	#insertValues(v)
	return "hello world"


@app.route('/reset')
def reset():
	v = makeValues()
	resetValues(v)
	return "reset"

### API REST THING ################################################################

@auth.verify_password
def verify(username, password):
	if not (username and password):
		return False
	return USER_DATA.get(username) == password

class GF(Resource):
	@auth.login_required
	def get(self):
		v = makeValues()
		print(v)
		GOOGLE_FEELS = {
			'feel1': {'interruption': v["ic"]},
			'feel2': {'frustration': v["fc"]},
			'feel3': {'help': v["hc"]},
			'feel4': {'swears': v["sc"]}
		}
		return GOOGLE_FEELS

api.add_resource(GF, '/googlefeels')

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)
