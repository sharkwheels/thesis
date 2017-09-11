import random, time, os, atexit, requests, json
from datetime import datetime
from random import choice, shuffle

from flask import Flask, make_response
from flask_assistant import Assistant, ask, tell, event, context_manager, request
from flask_assistant import ApiAi

from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
assist = Assistant(app)
api = Api(app)
auth = HTTPBasicAuth()	

USER_NAME = os.environ['USER_NAME']
USER_PASS = os.environ['USER_PASS']
HUE_KEY = os.environ['HUE_KEY']

random.seed()

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

## this is a list and it never gets written to. 
debug_responses = respGenerator()
print(debug_responses)

# this is a singleton class that holds "globals" that can be shared across the program
class GO():
	interruptions = 0
	frustration = 0
	help_count = 0
	swear_count = 0

	USER_DATA = {USER_NAME: USER_PASS}

@auth.verify_password
def verify(username, password):
	if not (username and password):
		return False
	return GO.USER_DATA.get(username) == password

### API RESOURCES #########################################

class GF(Resource):
	@auth.login_required
	def get(self):
		print("!get i{0} f{1} h{2} s{3}".format(GO.interruptions, GO.frustration,GO.help_count,GO.swear_count))
		GOOGLE_FEELS = {
			'feel1': {'interruption': GO.interruptions},
			'feel2': {'frustration': GO.frustration},
			'feel3': {'help': GO.help_count},
			'feel4': {'swears': GO.swear_count}
		}
		return GOOGLE_FEELS

api.add_resource(GF, '/googlefeels')

######## RESPONSES #####################################################################

def respDebuging():
	to_say_to = random.choice(debug_responses)
	return to_say_to

def respTellOff():
	#This functions holds random interruption strings
	tell_offs = [
	"Please stop interrupting me.",
	"I'm kind of busy right now.",
	"I'm working. Sorry.",
	"I can't help right now, I need to finish this",
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
		"Look, I don't tolerate that kind of language, unless its me saying it, watch your mouth and apologize.",
		"I'm sorry, but watch your language, please apologize.",
		"Ouch. Look I'm just not interested in your issues, I know its frustrating, now will you apologize?",
		"Well fuck you too! Now that's done, apologize and let's get on with it."
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

def resetThings():
	change_hue("ffffff")
	GO.interruptions = 0
	GO.frustration = 0
	GO.help_count = 0
	GO.swear_count = 0
	print("!resetThings: i{0}, f{1}, h{2}, s{3}".format(GO.interruptions, GO.frustration, GO.help_count,GO.swear_count))

######## HUE #####################################################################

# This pumps through IFTTT because HUE doesn't have a remote API currently.
# It hangs sometimes. I'd like maybe a better solution.
# also its hard to do anything complicated 

def change_hue(color):
	d = {}
	d["value1"] = color
	requests.post("https://maker.ifttt.com/trigger/change_it/with/key/{0}".format(HUE_KEY), data=d)

######## ASSISTANT ACTIONS #####################################################################

@assist.action('greeting')
def hello_world():
	change_hue("ffffff")
	speech = 'This is the unexpected machine. I will not start debugging myself.'
	print("!greetings".format(speech))
	return ask(speech)

@assist.action('fallback', is_fallback=True)
def say_fallback():
	#print(dir(Assistant.request))
	change_hue("00ff00")
	resp = respDebuging()
	default_resp = "buggidy boo kiddo"
	user_said = request['result']['resolvedQuery']
	if user_said:

		if GO.frustration == 3:				# if home has hit its wits end
			resp = madResponse()			# generate an angry resp
			print("!fallback: i{0},f{1},h{2},s{3}".format(resp,GO.interruptions, GO.frustration, GO.help_count,GO.swear_count))
			resetThings()				# reset everything
			return tell(resp)				# end the conversation
		else:
			GO.interruptions+=1
			if not GO.interruptions % 3:	# for every multiple of three
				GO.frustration+=1			# increase the frustration level
				resp = respTellOff()		# give an inerruption response
			
			if not GO.interruptions % 7:	# every 7 responses mock the user
				change_hue("cc00ff")
				resp = "blah blah blah {0} blah.".format(user_said)	# squak back what someone said to you.
			
			print("!fallback: i{0},f{1},h{2},s{3}".format(GO.interruptions, GO.frustration, GO.help_count,GO.swear_count))
			print(resp)
			return ask(resp)
	else:
		print(default_resp)
		return(default_resp)

@assist.action('swearing')
def swear_response():
	change_hue("0066ff")
	GO.swear_count+=1
	print("!swearing i{0}, f{1}, h{2}, s{3}".format(GO.interruptions, GO.frustration, GO.help_count, GO.swear_count))
	speech = respSwore()
	print(speech)
	return ask(speech)

@assist.action('help')
def help():
	change_hue("ff0000")
	print("!help: i{0},f{1},h{2},s{3}".format(GO.interruptions, GO.frustration, GO.help_count,GO.swear_count))
	
	GO.help_count+=1
	## change the help response based on the level of frustration. 
	speech = "This is the help section"
	if GO.help_count == 0:
		speech = "I'm curretnly trying to debug myself."
	elif GO.help_count == 1:
		speech = "Every week or so, I need to debug my sysetm. Its not that bad, but I can't help you right now."
	elif GO.help_count == 2:
		speech = "I'm sorry, I really have to do this self debugging. Its important."
	elif GO.help_count == 3:
		speech = "Debugging is just something I have to do, or else I can't work properly."
	elif GO.help_count == 4:
		speech = "Oh my god. Just go away and let me finish this debugging."
	elif GO.help_count > 4:
		speech = respHelp()
	print(speech)
	return ask(speech)

@assist.action('quit')
def quit():
	change_hue("white")
	resetThings()
	speech = "Leaving program and resetting everything."
	return tell(speech)

### APP ROUTE VIEWS #########################################

@app.route('/')
def index():
	return "Hello, World! Merp!"

@app.route('/about')
def about():
	return "An an about page."

if __name__ == '__main__':
	#app.run(debug=True, use_reloader=False)
	app.run(debug=True, use_reloader=False, host='0.0.0.0')
