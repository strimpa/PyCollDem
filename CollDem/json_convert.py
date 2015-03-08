import json
from json import JSONEncoder
from CollDem.models import Message, CollDemUser, EvaluationSet
from CollDem.controllers import MessageController
from django.conf.urls.static import static
from django.core.exceptions import ObjectDoesNotExist

class CollDemEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, EvaluationSet):
			returnObject = {
				'evaluator':obj.evaluator,
				'comment':obj.comment
			}
			for evaluation in obj.evaluation_set.all():
				returnObject[evaluation.name] = evaluation.factor
			return returnObject

		if isinstance(obj, Message):
			controller = MessageController(obj)
			userName = 'Anonymous'
			if obj.author!=None:
				userName = obj.author.username
				
			returnObject = {
				'id':obj.guid,
				'author':userName,
				'avatar':CollDemUser.objects.get_pic(obj.author),
				'header':obj.header, 
				'text':obj.text,
				'can_delete':(obj.author == obj.requestUser),
				'evaluation':controller.getEvaluation(obj.requestUser),
				'completeDataLength':obj.completeDataLength
			}
			# for evalSet in obj.user_evaluation.all():
			# 	returnObject['evaluation'].append(self.default(evalSet))

			if hasattr(obj, 'twittermessage'):
				returnObject['twitter_id'] = obj.twittermessage.msg_id

			return returnObject

		return JSONEncoder.default(self, obj)