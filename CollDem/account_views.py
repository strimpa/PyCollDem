import json
import string

from django.shortcuts import render_to_response, render
from CollDem.models import CollDemUser, Message, CollDemUserManager
from CollDem.lang import lang
from forms import AccountForm, ImageForm, ProfileForm, RegisterForm, LoginForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import SetPasswordForm

def account(request):
	profileForm = ProfileForm()
	accountForm = AccountForm()
	if request.user.is_authenticated():
		profileForm = ProfileForm(instance=request.user)
		accountForm = AccountForm(instance=request.user)
		if request.method == "POST":
			if 'profile_form' in request.POST:
				profileForm = ProfileForm(request.POST, request.FILES, instance=request.user)
				if profileForm.is_valid():
					profileForm.save()
				
			if 'account_form' in request.POST:
				accountForm = AccountForm(request.POST, instance=request.user)
				if accountForm.is_valid():
					accountForm.save()

	return render(request, "account.html", {
		'profile_form':profileForm,
		'account_form':accountForm,
		'login_form':LoginForm()})

def register(request):
	register_form = RegisterForm();
#	password_form = SetPasswordForm();
	if request.method == "POST":
		register_form = RegisterForm(request.POST, request.FILES)
		if register_form.is_valid():
			the_user = CollDemUser.objects.create_user(
				register_form.cleaned_data['username'], 
				register_form.cleaned_data['email'])
			register_form = RegisterForm(request.POST, request.FILES, instance=the_user)
			register_form.save()

			from django.core.mail import send_mail
			send_mail('Please confirm your registration', lang('REG_CONFIRMATION_MAIL', the_user.username, the_user.guid), 'dont_reply@tuets.com', [the_user.email])
			return HttpResponseRedirect('/register/confirm/') # Redirect after POST

	return render(request, "register.html", {
		'register_form':register_form,
		'login_form':LoginForm()})

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
		'login_form':LoginForm()
		})

def login(request):
	loginForm = LoginForm()
	return render_to_response("login.html", {'login_form':loginForm})

def profile(request, userId=None, username=None):
	if (None==userId and None==username) or "me"==userId:
		CollDemUser.objects.set_user(request.user)
	else:
		if None!=username:
			try:
				found_user = CollDemUser.objects.get(username=username)
				CollDemUser.objects.set_user(found_user)
			except ObjectDoesNotExist:
				pass
		if None!=userId:
			try:
				found_user = CollDemUser.objects.get(guid=userId)
				CollDemUser.objects.set_user(found_user)
			except ObjectDoesNotExist:
				pass

	image_form = ImageForm()
	return render(request, "profile.html", {
		'user_controller':CollDemUser.objects,
		'login_form':LoginForm()
		})
