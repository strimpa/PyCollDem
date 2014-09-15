import json
import string

from django.shortcuts import render, render_to_response
from CollDem.models import CollDemUser, Message
from django.http import HttpResponse, HttpResponseRedirect
from CollDem.json_convert import CollDemEncoder
from forms import AnswerForm
from django.template import RequestContext
from django.utils import timezone
from CollDem.controllers import MessageController

def messages(request, userid=None, answer_to=None, msgid=None):
	messagesToShow = None
	if msgid!=None:
		messagesToShow = (Message.objects.filter(guid=msgid))
	elif answer_to!=None:
		messagesToShow = (Message.objects.filter(answer_to_id=answer_to))
	elif userid!=None:
		messagesToShow = (Message.objects.filter(author_id=userid, answer_to_id=None))
#		messagesToShow.append(Message.objects.filter(visible_to_users__contains=userid))
#		messagesToShow.append(Message.objects.filter(author__connections__contains=userid, visibility="CONNECTIONS"))
	else:
		messagesToShow = Message.objects.filter(visibility="PUBLIC")

	messagesToShow = messagesToShow.order_by('created_at')

	data = []
	if len(messagesToShow) > 0: 
		for msg in messagesToShow:
			msg.canDelete = (msg.author == request.user)
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
			userid = None
			if request.user.is_authenticated:
				userid = request.user.guid

			new_msg = Message(
				answer_to_id=answer_to,
				header=header, 
				text=text, 
				created_at=timezone.now(),
				author_id=userid,
				visibility=visValue)
			new_msg.guid=MessageController.createUniqueIDString(new_msg)
			new_msg.save()
	else:
		answer_form = AnswerForm()

	return render(request, 'answer_snippet.html', {
		'answer_form':answer_form, 
		}, 
		context_instance=RequestContext(request))