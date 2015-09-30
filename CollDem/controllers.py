import re, random

from CollDem.models import Message, CollDemUser, TwitterMessage
from devote.models import KeywordList, Keyword, Evaluation
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

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

		if msg.author!=None and msg.author.is_authenticated():
			savestring += "_"+msg.author.username[:20]
			if MessageController.isIdUnique(savestring):
				return savestring

		savestring += "_"
		savestring += str(int(random.random()*100000000))
		if MessageController.isIdUnique(savestring):
			return savestring

		return None

	@classmethod
	def createMessage(cls, answer_to, header, text, request, visValue, twitter_id=None):
		userid = None
		if request.user.is_authenticated():
			userid = request.user.guid

		new_msg = None
		new_msg = Message(
			answer_to_id=answer_to,
			header=header, 
			text=text, 
			created_at=timezone.now(),
			author_id=userid,
			visibility=visValue)

		new_msg.guid=cls.createUniqueIDString(new_msg)
		new_msg.save()

#		KeywordList.mgr.CreateForTarget(new_msg)

		return new_msg

	def __init__(self, msg):
		self.myMsg = msg

	def mayUserInteract(self, user):
		if not user.is_authenticated():
			return False
		return \
			self.myMsg.visibility=="PUBLIC" or \
			(self.myMsg.visibility=="CONNECTIONS" and self.myMsg.author in user.connections.all()) or \
			(self.myMsg.guid in user.visible_messages.all().values('guid'))
		