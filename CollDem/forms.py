from django import forms
from django.forms import ModelForm
from CollDem.models import (CollDemUser, Message)

class LoginForm(forms.Form):
	username = forms.CharField(max_length=100)
	password = forms.CharField(widget=forms.PasswordInput(render_value=True))

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
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
	class Meta:
		model = CollDemUser
		fields = ['username', 'email', 'pic', 'first_name', 'last_name']

	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2
	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super(RegisterForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

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
