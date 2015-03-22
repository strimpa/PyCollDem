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
				'is_author':(obj.author == obj.requestUser),
				'evaluation':controller.getEvaluation(obj.requestUser),
			}
			if hasattr(obj, 'completeDataLength'):
				returnObject['completeDataLength'] = obj.completeDataLength

			return returnObject

		return JSONEncoder.default(self, obj)