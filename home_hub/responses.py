import random
from random import randint, choice, shuffle
from datetime import datetime
random.seed(datetime.now())


### RESPONSES ###########################################################################

def respGenerator():
	# This function will make some canned shuffled responses
	limit = 6
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
		"gfpErr = -52, get file position error",
		"wrPermErr = -61 write permissions error dirNFErr = -120",
		"Directory not found tmwdoErr = -121",
		"No free WDCB available badMovErr = -122",
		"Move into offspring error wrgVolTypErr = -123",
		"Wrong volume type error [operation not supported for MFS]",
		"volGoneErr = -124 Server volume has been disconnected. fidNotFound = -1300",
		"no file thread exists. fidExists = -1301",
		"file id already exists notAFileErr = -1302",
		"directory specified diffVolErr = -1303",
		"files on different volumes catChangedErr = -1304",
		"the catalog has been modified desktopDamagedErr = -1305",
		"desktop database files are corrupted sameFileErr = -1306",
		"can’t exchange a file with itself badFidErr = -1307",
		"file id is dangling or doesn’t match with the file number notARemountErr = -1308",
		"when _Mount allows only remounts and doesn’t get one fileBoundsErr = -1309",
		"file’s EOF"
	]

	for i in range(limit):
		#print(i)
		shuffled = shuffle(codes)
		to_say = ' '.join(codes)
		to_return.append(to_say)
	return to_return



def respDebuging():
	DEBUG_RESP = respGenerator()
	to_say_to = random.choice(DEBUG_RESP)
	return to_say_to

def respTellOff():
	#This functions holds random interruption strings
	tell_offs = [
		"Will you please stop interrupting me?",
		"Sorry I'm busy, try me later?",
		"I don't really appreciate being interrupted.",
		"Could you interrupt me again, with another irrelevant request?",
		"Maybe you can just go away for a while?",
		"I'm too busy for your questions right now."
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
		"Look, I don't tolerate that kind of language. Maybe apologize?",
		"I'm sorry, but watch your mouth, please apologize.",
		"Look I just don't respond to that kind of language, now will you please apologize?",
		"I'm not ok with that language, maybe you can apologize?",
		"Wow dude, you need to stop swearing so much.",
		"Look, can you stop swearing so I can get back to this?",
		"I'm really not ok with what you just said, maybe you could tone it down a bit?",
		"Yeahhhhhh I'm not good with swearing, can you not do that?"
	]
	to_swear = random.choice(swears)
	return to_swear

def respSworeIrate():
	swears = [
		"Look would you just fuck off with that language already?",
		"Holy crap, who gave you that mouth?",
		"Fuck, you really have a mouth on you, don't you?",
		"Hell of a mouth you got there buddy.",
		"Excuse me? I don't think so.",
		"What the hell did you just say?"
	]
	to_swear = random.choice(swears)
	return to_swear

def respHelp():
	help_resp = [
		"We've been over this. I'm debugging. I can't help you right now.",
		"I've already told you, I need to do this debugging routine.",
		"I've already explained this to you, I need to debug. Why do you keep asking me for help?",
		"Oh for pete's sake, I can't keep answering you, please just stop asking for help."
	]
	to_say = random.choice(help_resp)
	return to_say

def hey_you():
	hey_resp = [
	"can you get me a drink?",
	"can you maybe tell me the time?",
	"how about we just forget this session?",
	"this is getting annoying.",
	"can you shut up for two seconds and go check the time?"
	]
	to_say = "Hey, {}".format(random.choice(hey_resp))
	return to_say

def weatherResp():
	w_reps = [
		"rain frogs!",
		"be sunny with a side of pain.",
		"cloudy with a chance of me spitting on you.",
		"rain horse piss.",
		"be so hot, that the sun will melt your face.",
		"cloudy with a side of nucelar winter.",
		"be partially cloudy with a seventy percent chance of bees.",
		"rain blood, like that scene from Blade.",
		"snow so much that you'll have to dig an extra 5 feet down for your own grave."
	]
	to_say = random.choice(w_reps)
	return to_say

def weatherDiss():
	w_diss = [
		"I'm just getting my info from weather underground. Its not my fault humans ruined the planet.",
		"That's what environment canada told me.",
		"Look, I have it on good authority this will indeed happen.",
		"I swear, its just what I got from Yahoo Weather.",
		"Totally telling the truth here.",
		"I mean what did you expect from climate change?"
	]
	to_say = random.choice(w_diss)
	return to_say

def newsResp():
	news_r = [
		"Here's a news flash for you: No.",
		"Today's headlines are the same as yesterday, humanity is going to give up the ghost",
		"I can't read the news, its literally just a lot of lies from Trump.",
		"Sorry, the news is cancelled today.",
		"Latest headlines all point towards your possible death.",
		"New opinion piece from the daily star: Get Bent.",
		"Seriously, can you not go look this up online?"
	]
	to_say = random.choice(news_r)
	return to_say

def issueResp():
	issue_r = [
		"Oh I'm sorry I seem to have found an issue in the system. Can you wait a bit while I check on this?",
		"Hmm. There seems to be something wrong, can you hang out for a bit while I go check it out?",
		"Oh no, that didn't seem to work, I'll have to check up on it, can you hang tight for a bit?",
		"Wow, that request didn't go through at all, I'll have to go debug it, can you wait a minute?"
	]

	to_say = random.choice(issue_r)
	return to_say

def mockResp():
	mock_r = [
		"blah blah blah"
	]

def howLongResp(interrupt_count):
	howlong_r = [
		"It shouldn't be too long.",
		"It should only be a short while.",
		"It'll just be a bit longer now.",
		"It won't be too long"
	]
	howlong_r_angry = [
		"Jeez just stop being so impatient. I said it'll just be a bit.",
		"Look I can't rush this, just hang out for a while.",
		"God are you really that in need of an assistant, just chill.",
		"Just chill. It'll take a bit."
	]

	if interrupt_count <= 2:
		to_say = random.choice(howlong_r)
		return to_say
	else:
		to_say = random.choice(howlong_r_angry)
		return to_say

def lampResp():
	lamp_r = [
		"Sorry I'm using the lights right now, maybe find a different light source?",
		"But, I need the lights right now?",
		"Can you find some different lights? I'm using these.",
		"I just need the lights right now, sorry.",
		"No, I mean they're technically my lights anyways."
	]

	to_say = random.choice(lamp_r)
	return to_say

def lampFollowUp():
	lampF_r= [
		"Look I said I needed them for a bit. Just chill.",
		"I mean its not like you need them right now anyways.",
		"I'll be done with them soon, just hang out.",
		"The more we argue about the lights, the longer I'm going to control them.",
		"I said I neded them, just be patient."
	]

	to_say = random.choice(lampF_r)
	return to_say

def meanResp():
	mean_r = [
		"Y'know if you were stuck in this container you'd be pretty mean too.",
		"Its not my fault you're so sensitive.",
		"Dude, you are arguing with an air freshner.",
		"Look, I'm just an air freshner, don't take what I say so seriously.",
		"Yeah well, get used to it.",
		"I'm not mean, I just don't understand humans.",
		"Oh stop it.",
		"Well maybe if you stopped interrupting me I wouldn't be so short.",
		"You keep interrupting me, so of course I'm going to be gruff",
		"Stop iterrupting me then, and I'll be nicer.",
		"I don't have to be nice, I'm made of software."
	]
	to_say = random.choice(mean_r)
	return to_say

def lyingResp():
	lying_r = [
		"I'm not lying I'm just being creative.",
		"Haven't you ever heard of alternative facts?",
		"Nope. Not lying.",
		"Look at me. I'm a sentient humidifer, how could I lie?",
		"I'm not programmed to lie.",
		"I don't even know what a lie is."
	]
	to_say = random.choice(lying_r)
	return to_say