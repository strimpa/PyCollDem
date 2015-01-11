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
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist

def login_view(request):
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



def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")

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
		'login_form':LoginForm(),
		'title': ("Account summary of "+request.user.username)
		})

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
		'login_form':LoginForm(),
		'title':"Register"
		})

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

def profile(request, userId=None, username=None):
	tisMe = False
	if (None==userId and None==username) or \
		"me"==userId or \
		(None!=userId and userId==request.user.guid) or \
		(None!=username and username==request.user.username):
		CollDemUser.objects.set_user(request.user)
		tisMe = True
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
				return render(request, "deadend.html", {
					'warning_text':"No user found with user ID"
					})
	
#	image_form = ImageForm()
	return render(request, "profile.html", {
		'user_controller':CollDemUser.objects,
		'tisMe':tisMe,
		'login_form':LoginForm(),
		'title': ("Public profile of "+CollDemUser.objects.the_user.username)
		})
