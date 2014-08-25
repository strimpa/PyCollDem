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
		header = request.POST['header']
		text = request.POST['text']
		entermsg_form = EnterMessageForm(request.POST)

		if entermsg_form.is_valid():
			visValue = entermsg_form.cleaned_data['visibility']
			userid = None
			if request.user.is_authenticated:
				userid = request.user.id
				
			new_msg = Message(
				header=header, 
				text=text, 
				created_at=timezone.now(),
				author_id=userid,
				visibility=visValue)
			new_msg.save()

	return entermsg_form

def home(request):
	entermsg_form = None
	logon_form = None

	user = request.user

	logon_form = handleUserForm(request)
	entermsg_form = handleMessageForm(request)

	MessageFormSet = modelformset_factory(Message, fields=['header', 'text'], widgets={'text':Textarea()})
	message_formset = MessageFormSet(queryset=Message.objects.all())

	return render(request, 'home.html', {
		'logon_form':logon_form, 
		'entermsg_form':entermsg_form, 
		'message_formset':message_formset, 
		}, 
		context_instance=RequestContext(request))



def logout_view(request):
	logout(request)
	return redirect("/")