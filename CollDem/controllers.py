import re, random

from CollDem.models import Message, CollDemUser
from django.conf import settings

class MessageController:
	
	############################
	# Helpers
	@classmethod
	def isIdUnique(cls, id):
		occurrances = Message.objects.filter(guid=id)
		return len(occurrances)==0

	@classmethod
	def createUniqueIDString(cls, msg):
		pattern = re.compile('[^\w]')
		savestring = pattern.sub('_', msg.header)

		#go through steps findign the first unique one
		savestring = savestring[:100]
		if MessageController.isIdUnique(savestring):
			return savestring

		savestring += "_"+msg.author.username[:20]
		if MessageController.isIdUnique(savestring):
			return savestring

		savestring += "_"
		savestring += str(int(random.random()*100000000))
		if MessageController.isIdUnique(savestring):
			return savestring

		return None

class UserController:
	"Class to manage user instances"

	def __init__(self, user):
		self.the_user = user

	def valid_user(self):
		return isinstance(self.the_user, CollDemUser)

	def get_pic(self):
		"logic to access the picture or get default one if undefined"
		if 	not self.valid_user() or None==self.the_user.pic.url:
			return '/static/images/users/default_pic.gif'
		return '/media/'+settings.MEDIA_URL+self.the_user.pic.url

	def get_stats(self):
		if 	not self.valid_user():
			return None
		stats = {}
		user_msgs = Message.objects.filter(author=self.the_user)
		stats['msg_count'] = len(user_msgs)
		rootMsgCount = len(user_msgs.filter(answer_to=None))
		stats['answer_count'] = stats['msg_count'] - rootMsgCount
		return stats
