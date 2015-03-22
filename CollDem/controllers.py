import re, random

from CollDem.models import Message, CollDemUser, KeywordList, Keyword, Evaluation, TwitterMessage
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
	def AddEvalKeyword(cls, msg, keyword):
		try:
			keywords = KeywordList.objects.get(for_msg=msg)
		except ObjectDoesNotExist:
			keywords = KeywordList.objects.create(msg)
			keywords.save()

		try:
			key = Keyword.objects.get(name=keyword)
		except ObjectDoesNotExist:
			key = Keyword.objects.create(name=keyword)
		keywords.keyword_set.add(key)
		keywords.save()

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

		keywords = KeywordList.objects.create(for_msg=new_msg)
		keywords.save()
		for defaultKeyTuple in Evaluation.EVAL_DEFAULT_CHOICES:
			cls.AddEvalKeyword(new_msg, defaultKeyTuple[1])

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

	def getEvaluation(self, user=None):
		evaluation = {}
		evaluation['summary'] = {}
		evaluation['keywords'] = []
		try:
			for keyword in self.myMsg.keywordlist.keyword_set.all().values("name"):
				evaluation['keywords'].append(keyword['name']);
		except:
			pass
		evaluation['can_evaluate'] = None!=user and user.is_authenticated() and self.myMsg.author != user
		evaluation['activeUserEvaluation'] = {}
		for es in self.myMsg.user_evaluation.all():
			for e in es.evaluation_set.all():
				if not (e.name in evaluation['keywords']):
					continue

				if None!=user and es.evaluator == user:
					evaluation['activeUserEvaluation'][e.name] = e.factor

				try:
					evaluation['summary'][e.name] += e.factor
				except KeyError:
					evaluation['summary'][e.name] = e.factor

		for key,val in evaluation['summary'].iteritems():
			evaluation['summary'][key] = val/len(self.myMsg.user_evaluation.all())

		return evaluation

	def setKeywords(self, keys):
		keySet, created = KeywordList.objects.get_or_create(for_msg=self.myMsg)
		keySet.keyword_set.clear()

		for key in keys:
			evaluation, created = Keyword.objects.get_or_create(name=key)
			keySet.keyword_set.add(evaluation)

		#default values
		for defValIndex in range(0, len(Evaluation.EVAL_DEFAULT_CHOICES)):
			defVal = Evaluation.EVAL_DEFAULT_CHOICES[defValIndex][1]
			if defValIndex >= keySet.keyword_set.count():
				evaluation, created = Keyword.objects.get_or_create(name=defVal)
				keySet.keyword_set.add(evaluation)

		keySet.save()
		return True

		