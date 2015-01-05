import json
import string

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Q
from CollDem.models import CollDemUser, Message, Evaluation, EvaluationSet
from CollDem.json_convert import CollDemEncoder
from forms import AnswerForm
from CollDem.controllers import MessageController
from django.core.exceptions import ObjectDoesNotExist

def messages(request, authorid=None, userid=None, answer_to=None, msgid=None):
	messagesToShow = None
	if msgid!=None:
		messagesToShow = (Message.objects.filter(guid=msgid))
	elif authorid!=None:
		messagesToShow = (Message.objects.filter(author_id=authorid, answer_to_id=answer_to))
	elif userid!=None and userid!="0":
		messagesToShow = Message.objects.filter(
			Q(visibility="PUBLIC") |
			Q(visibility="CONNECTIONS", author__in=request.user.connections.all()) |
			Q(visibility="USERS", guid__in=request.user.visible_messages.all().values('guid')), 
			answer_to_id=answer_to)
			
#		messagesToShow = messagesToShow.exclude(author=request.user)
	else:
		messagesToShow = Message.objects.filter(visibility="PUBLIC", answer_to_id=answer_to)

	messagesToShow = messagesToShow.order_by('-created_at')
	completeDataLength = len(messagesToShow)

	if 'offset' in request.POST:
		lowerlimit = int(request.POST['offset'])
		upperLimit = lowerlimit+2
		messagesToShow = messagesToShow[lowerlimit:upperLimit]

	data = []
	if len(messagesToShow) > 0: 
		for msg in messagesToShow:
			msg.requestUser = request.user
			msg.completeDataLength = completeDataLength
			messageJsonObj = json.dumps(msg, cls=CollDemEncoder)
			data.append(messageJsonObj)

	dataString = '[' + string.join(data, ',') + ']'

	return HttpResponse(dataString, content_type='application/json')

def delete(request, msgid):
	message = Message.objects.get(guid=msgid)
	if request.user != message.author:
		return HttpResponseRedirect('/login')

	returnValue = "deleted"
	if len(message.answers.all())>0:
		message.header="Deleted Message"
		message.text="For keeping the content tree working, this message has not been deleted but voided."
		message.save()
		returnValue = "voided"
	else:
		message.delete()

	return HttpResponse(returnValue, content_type='text/plain')


def answer(request):
	if request.method=='POST' and 'text' in request.POST:
		answer_form = AnswerForm(request.POST)
		if answer_form.is_valid():
			answer_to = request.POST['msgID']
			answer_to_msg = Message.objects.get(guid=answer_to)
			header = "RE:"+answer_to_msg.header

			visValue = answer_form.cleaned_data['visibility']
			text = answer_form.cleaned_data['text']
			MessageController.createMessage(answer_to, header, text, request, visValue)
	else:
		answer_form = AnswerForm()

	return render(request, 'answer_snippet.html', {
		'answer_form':answer_form, 
		}, 
		context_instance=RequestContext(request))

def evaluation(request, msgid=None):
	return render(request, 'evaluationImage.svg', {})

def evaluate(request, msgid):
	# if request.method!='POST':
	# 	return HttpResponse("BAD EVALUATION REQUEST", content_type='text/plain')
	msg = Message.objects.get(guid=msgid)
	msgController = MessageController(msg)

	if not msgController.mayUserInteract(request.user):
		data = json.dumps(msgController.getEvaluation())
		return HttpResponse(data, content_type='application/json')

	try:
		evalSet = EvaluationSet.objects.get(evaluator=request.user, target_msg=msg)
	except ObjectDoesNotExist:
		evalSet = EvaluationSet.objects.create(evaluator=request.user, target_msg=msg)

	for postVarKey,postVarVal in request.POST.items():
		evaluation = None
		try:
			evaluation = evalSet.evaluation_set.get(name=postVarKey)
			evaluation.factor = float(postVarVal)
			evaluation.save()
		except ObjectDoesNotExist:
			evaluation = Evaluation.objects.create(name=postVarKey, factor=float(postVarVal), evaluation_set=evalSet)
	evalSet.save()

	data = json.dumps(msgController.getEvaluation(request.user))

	return HttpResponse(data, content_type='application/json')