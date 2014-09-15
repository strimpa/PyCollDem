import json
import string

from django.shortcuts import render_to_response, render
from CollDem.models import CollDemUser, Message
from CollDem.controllers import UserController
from forms import AccountForm, ImageForm, ProfileForm, RegisterForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist

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
		'account_form':accountForm})

def register(request):
	register_form = RegisterForm();
	if request.method == "POST":
		register_form = RegisterForm(request.POST, request.FILES)
		if register_form.is_valid():
			register_form.save()
	return render(request, "register.html", {
		'register_form':register_form})


def login(request):
	loginForm = LoginForm()
	return render_to_response("login.html", {'login_form':loginForm})

def profile(request, userId=None, username=None):
	user_controller = UserController(None)
	if None==userId or "me"==userId:
		user_controller = UserController(request.user)
	else:
		if None!=username:
			try:
				found_user = CollDemUser.objects.get(username=username)
				user_controller = UserController(found_user)
			except ObjectDoesNotExist:
				pass
		if None==userId:
			try:
				found_user = CollDemUser.objects.get(guid=userId)
				user_controller = UserController(found_user)
			except ObjectDoesNotExist:
				pass

	image_form = ImageForm()
	return render(request, "profile.html", {
		'user_controller':user_controller})
