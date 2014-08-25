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
#		fields = ['username', 'password']

class EnterMessageForm(forms.Form):
	header = forms.CharField(max_length=256)
	text = forms.CharField(max_length=1024, widget=forms.Textarea, label="")
	visibility = forms.ChoiceField(widget=forms.Select, choices=Message.VISIBILITY_CHOICES)

