import re

values = {
	'REG_CONFIRMATION': 'Please check your mail and confirm your membership.',
	'REG_CONFIRMATION_SUBMITTED': 'Hey, hi %0! <br />You\'re now activated and you can log-in above.',
	'REG_CONFIRMATION_MAIL': 'Hi %0 Please confirm your membership by clicking on this link: http://tuets.com/registration/confirm/%1',
	'REG_CONFIRMATION_FAILED': 'The user with the ID could not be found. You might already be activated, or please try registering again.'
}

args = []

def replaceFunc(match):
	"insert parameters into strings"
	index = int(match.group(1))
	return str(args[index])

def lang(key, *var_args):
	global args
	args = var_args
	print args
	val = values[key]
	p = re.compile(r'%(\d)')
	val = p.sub(replaceFunc, val)
	return val