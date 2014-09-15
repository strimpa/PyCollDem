from django import forms
from django.forms import ModelForm
from CollDem.models import (CollDemUser, Message)

class LogOnForm(ModelForm):
	class Meta:
		model = CollDemUser
		fields = ['username', 'password']

class AccountForm(ModelForm):
	class Meta:
		model = CollDemUser
		fields = ['first_name', 'last_name', 'email']
	account_form = forms.BooleanField(widget=forms.HiddenInput, required=False)

class ProfileForm(ModelForm):
	class Meta:
		model = CollDemUser
		fields = ['username', 'pic']
	profile_form = forms.BooleanField(widget=forms.HiddenInput, required=False)

class RegisterForm(ModelForm):
	class Meta:
		model = CollDemUser
		fields = ['first_name', 'last_name', 'email', 'username', 'pic']

class EnterMessageForm(forms.Form):
	header = forms.CharField(max_length=256, label="")
	text = forms.CharField(max_length=1024, widget=forms.Textarea, label="")
	visibility = forms.ChoiceField(widget=forms.Select, choices=Message.VISIBILITY_CHOICES, label="")
	visible_to_users = forms.CharField(max_length=1024, label="", required=False)

class AnswerForm(forms.Form):
	text = forms.CharField(max_length=1024, widget=forms.Textarea, label="")
	visibility = forms.ChoiceField(widget=forms.Select, choices=Message.VISIBILITY_CHOICES, label="")
	visible_to_users = forms.CharField(max_length=1024, label="", required=False)

class ImageForm(forms.Form):
	pic = forms.ImageField()
