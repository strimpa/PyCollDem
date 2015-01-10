from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import Textarea
from django.forms.models import modelformset_factory

from CollDem.forms import LoginForm, EnterMessageForm
from CollDem.models import Message, CollDemUser
from CollDem.controllers import MessageController
from CollDem.analytics import notification_list

class LoginError(Exception):
	def __init__(self, value):
		self.value = value
	def __unicode__(serlf):
		return repr(self.value)

def handleUserForm(request):
	login_form = LoginForm()
	if request.method=='POST' and 'username' in request.POST and 'password' in request.POST:
		login_form = LoginForm(data=request.POST)
		if login_form.is_valid():
			username = login_form.cleaned_data['username']
			password = login_form.cleaned_data['password']

			user = authenticate(username=username, password=password)
			if not user.is_active or user is None:
				raise LoginError('REG_CONFIRMATION_FAILED')
			
			login(request, user)

	return login_form

def handleMessageForm(request):
	entermsg_form = EnterMessageForm()
	if request.method=='POST' and 'header' in request.POST and 'text' in request.POST:
		entermsg_form = EnterMessageForm(request.POST)

		if entermsg_form.is_valid():
			visValue = entermsg_form.cleaned_data['visibility']
			header = entermsg_form.cleaned_data['header']
			text = entermsg_form.cleaned_data['text']
			MessageController.createMessage(None, header, text, request, visValue)

	return entermsg_form

def home(request, urlMsgId=""):
	entermsg_form = None
	login_form = None

	user = request.user

	try:
		login_form = handleUserForm(request)
	except:
		return HttpResponseRedirect('/register/confirm/')

	entermsg_form = handleMessageForm(request)

	MessageFormSet = modelformset_factory(Message, fields=['header', 'text'], widgets={'text':Textarea()})
	message_formset = MessageFormSet(queryset=Message.objects.all())

	return render(request, 'home.html', {
		'login_form'			: login_form, 
		'entermsg_form'			: entermsg_form, 
		'message_formset'		: message_formset, 
		'no_message_selected'	: urlMsgId=="",
		'urlMsgId' 				: urlMsgId,
		'title'					: ( "Your messages" if user.is_authenticated() else "Public messages")
		}, 
		context_instance=RequestContext(request))



def logout_view(request):
	logout(request)
	return redirect("/")

def notification_view(request):
	notifications = notification_list(request.user)

	request.user.last_update = timezone.now()
	request.user.save()

	return render(request, 'notifications.html', 
		{
		'notifications': notifications,
		'title' 	   : "Notifications"
		})
