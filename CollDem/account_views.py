import json
import string

from django.shortcuts import render_to_response, render
from CollDem.models import CollDemUser, Message, CollDemUserManager
from CollDem.lang import lang
from CollDem.forms import AccountForm, ImageForm, ProfileForm, RegisterForm, LoginForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist

def login_request(request):
	login_form = LoginForm(data=request.POST)
	if login_form.is_valid():
		username = login_form.cleaned_data['username']
		password = login_form.cleaned_data['password']

		try:
			user = CollDemUser.objects.get(username=username)
		except ObjectDoesNotExist:
			return render(request, "deadend.html", {
							'login_form':LoginForm(),
							'warning_text':"No user with that name."
							})

		authenticated_user = authenticate(username=username, password=password)
		if authenticated_user is None:
			# no user with that name
			warning_text = "Wrong password."
			return render(request, "deadend.html", {
							'login_form':LoginForm(),
							'warning_text':warning_text
							})

		#user isn't activated yet
		if not authenticated_user.is_active:
			#user isn't activated yet
			return render(request, "deadend.html", {
							'login_form':LoginForm(),
							'warning_text':"User hasn't been activated yet. Please check your email."
							})

		# SUCCESS!
		login(request, authenticated_user)
		return HttpResponseRedirect('/') # Redirect after POST

	return render(request, "deadend.html", {
		'login_form':LoginForm(),
		'warning_text':"Login failed - please try again."
		})



def logout_request(request):
	logout(request)
	return HttpResponseRedirect("/")

def follow(request, userId):
	returnValue = "failed"
	if request.user.is_authenticated():
		try:
			found_user = CollDemUser.objects.get(guid=userId)
			request.user.connections.add(found_user)
			returnValue = "succeeded"
		except:
			pass

	return HttpResponse(returnValue, content_type='text/plain')

def registerConfirm(request, userId=''):
	confirmation_text = lang('REG_CONFIRMATION')
	if ''!=userId:
		try:
			usr = CollDemUser.objects.get(guid=userId)
			usr.is_active = True
			usr.save()
			confirmation_text = lang('REG_CONFIRMATION_SUBMITTED', usr.username)
		except ObjectDoesNotExist:
			confirmation_text = lang('REG_CONFIRMATION_FAILED')

	return render(request, "register.html", {
		'confirmation':True,
		'confirmation_text':confirmation_text,
		'login_form':LoginForm(),
		'title':"Register"
		})
