import json
from json import JSONEncoder
from CollDem.models import Message, CollDemUser, EvaluationSet
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
			returnObject = {
				'id':obj.guid,
				'author':obj.author.username,
				'avatar':CollDemUser.objects.get_pic(obj.author),
				'header':obj.header, 
				'text':obj.text,
				'can_delete':obj.canDelete,
				'evaluation':{}
			}
			for evalSet in obj.user_evaluation.all():
				returnObject['evaluation'].append(self.default(evalSet))

			return returnObject

		return JSONEncoder.default(self, obj)