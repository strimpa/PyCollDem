from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.http import HttpResponse
from django.forms import Textarea
from django.forms.models import modelformset_factory
from django.utils import timezone

from CollDem.forms import LogOnForm, EnterMessageForm
from CollDem.models import Message, CollDemUser
from CollDem.controllers import MessageController

def handleUserForm(request):
	logon_form = LogOnForm()
	if request.method=='POST' and 'username' in request.POST and 'password' in request.POST:
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(request, user)
		else:
			logon_form = LogOnForm(data=request.POST)
	return logon_form

def handleMessageForm(request):
	entermsg_form = EnterMessageForm()
	if request.method=='POST' and 'header' in request.POST and 'text' in request.POST:
		entermsg_form = EnterMessageForm(request.POST)

		if entermsg_form.is_valid():
			visValue = entermsg_form.cleaned_data['visibility']
			header = entermsg_form.cleaned_data['header']
			text = entermsg_form.cleaned_data['text']
			userid = None
			if request.user.is_authenticated:
				userid = request.user.guid

			new_msg = Message(
				header=header, 
				text=text, 
				created_at=timezone.now(),
				author_id=userid,
				visibility=visValue)
			new_msg.guid=MessageController.createUniqueIDString(new_msg)
			new_msg.save()

	return entermsg_form

def home(request, urlMsgId=""):
	entermsg_form = None
	logon_form = None

	user = request.user

	logon_form = handleUserForm(request)
	entermsg_form = handleMessageForm(request)

	MessageFormSet = modelformset_factory(Message, fields=['header', 'text'], widgets={'text':Textarea()})
	message_formset = MessageFormSet(queryset=Message.objects.all())

	return render(request, 'home.html', {
		'logon_form'			: logon_form, 
		'entermsg_form'			: entermsg_form, 
		'message_formset'		: message_formset, 
		'no_message_selected'	: urlMsgId=="",
		'urlMsgId' 				: urlMsgId
		}, 
		context_instance=RequestContext(request))



def logout_view(request):
	logout(request)
	return redirect("/")