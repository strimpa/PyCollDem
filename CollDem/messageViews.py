import json
import string

from django.utils import timezone
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Q
from CollDem.models import CollDemUser, Message
from CollDem.json_convert import CollDemEncoder
from forms import AnswerForm
from CollDem.controllers import MessageController
from django.core.exceptions import ObjectDoesNotExist

from devote.models import Evaluation, EvaluationSet, KeywordList, Keyword

global_loading_step = 8
answer_loading_step = 3

def messages(request, authorid=None, userid=None, answer_to=None, msgid=None):
	messagesToShow = None
	is_answerlist_query = (answer_to!=None)
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
		upperLimit = lowerlimit+global_loading_step
		if is_answerlist_query:
			upperLimit = lowerlimit+answer_loading_step
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


def render_msg(request, msgid):
	the_msg = Message.objects.get(guid=msgid)

	devote_obj = EvaluationSet.mgr.getEvaluation(msgid, request.user)
	devote_obj['can_evaluate'] = request.user.is_authenticated() and the_msg.author != request.user
	devote_obj['is_author'] = request.user.is_authenticated() and the_msg.author == request.user

	return render(request, 'message.html', {
		'msg':the_msg,
		'is_anonymous': the_msg.author == None,
		'user_is_author': (the_msg.author == request.user),
		'avatar': CollDemUser.objects.get_pic(the_msg.author),
		'eval_url':"devote/render_eval/"+the_msg.guid,
		'devote_data':devote_obj
		})