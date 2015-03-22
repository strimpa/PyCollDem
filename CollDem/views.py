from twython import Twython

import lang

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import Textarea
from django.forms.models import modelformset_factory

from CollDem.forms import LoginForm, EnterMessageForm, AccountForm, ImageForm, ProfileForm, RegisterForm, LoginForm
from CollDem.models import Message, CollDemUser, SocialNetwork, Evaluation
from CollDem.controllers import MessageController
from CollDem.analytics import notification_list

from django.conf import settings

class LoginError(Exception):
	def __init__(self, value):
		self.value = value
	def __unicode__(serlf):
		return repr(self.value)

def handleMessageForm(request):
	data = {'keywords':",".join([Evaluation.EVAL_DEFAULT_CHOICES[i][1] for i in range(len(Evaluation.EVAL_DEFAULT_CHOICES))])}
	entermsg_form = EnterMessageForm(initial=data)
	
	if request.method=='POST' and 'header' in request.POST and 'text' in request.POST:
		entermsg_form = EnterMessageForm(request.POST)

		if entermsg_form.is_valid():
			visValue = entermsg_form.cleaned_data['visibility']
			header = entermsg_form.cleaned_data['header']
			text = entermsg_form.cleaned_data['text']
			twitter_id = entermsg_form.cleaned_data['twitter_id']
			keywords = entermsg_form.cleaned_data['keywords']
			if twitter_id=='':
				twitter_id = None
			msg = MessageController.createMessage(None, header, text, request, visValue, twitter_id)
			msgController = MessageController(msg)
			keyWordArray = keywords.split(',')
			msgController.setKeywords(keyWordArray)

	return entermsg_form

def handleOAuth(request):
	twitter = Twython(settings.APP_KEY, settings.APP_SECRET)
	try:
		auth = twitter.get_authentication_tokens(callback_url=settings.TWITTER_CALLBACK)
	
		request.session['OAUTH_TOKEN'] = auth['oauth_token']
		request.session['OAUTH_TOKEN_SECRET'] = auth['oauth_token_secret']

		return auth['auth_url']
	except TwythonAuthError:
		pass
	return None

def handleOAuthAppOnly():
	twitter = None

	try:
	    twitter_network = SocialNetwork.objects.get(name="Twitter")
	    twitter = Twython(settings.APP_KEY, access_token=twitter_network.acces_token)
	except Exception, e:
		return None
    
	twitter = Twython(settings.APP_KEY, settings.APP_SECRET, oauth_version=2)
	if None==twitter:
		return None

	try:
		access_token = twitter.obtain_access_token()
	except TwythonAuthError:
		return None

	twitter_network = SocialNetwork.objects.create(
		name="Twitter", 
		description="128 character exibitionism",
		home="http://www.twitter.com",
		access_token=access_token)
	twitter = Twython(settings.APP_KEY, access_token=access_token)
	return twitter

def home(request, urlMsgId=""):
	entermsg_form = None
	login_form = None

	user = request.user

	entermsg_form = handleMessageForm(request)

	MessageFormSet = modelformset_factory(Message, fields=['header', 'text'], widgets={'text':Textarea()})
	message_formset = MessageFormSet(queryset=Message.objects.all())

#	auth_url = handleOAuth(request)

	twitter = handleOAuthAppOnly()
#	search_result = twitter.search(q='gunchirp')

	return render(request, 'home.html', {
		'login_form'			: LoginForm(), 
		'entermsg_form'			: entermsg_form, 
		'message_formset'		: message_formset, 
		'no_message_selected'	: urlMsgId=="",
		'urlMsgId' 				: urlMsgId,
#		'search_result'			: search_result,
		'title'					: ( "Your messages" if user.is_authenticated() else "Public messages")
		}, 
		context_instance=RequestContext(request))


def notification_view(request):
	if request.user==None or not request.user.is_authenticated():
		return render(request, "deadend.html", {
			'login_form':LoginForm(),
			'warning_text':"User must be logged in to see notifications."
		})

	notifications = notification_list(request.user)

	request.user.last_update = timezone.now()
	request.user.save()

	return render(request, 'notifications.html', 
		{
		'notifications': notifications,
		'title' 	   : "Notifications"
		})


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
	
	#oauth
	if request.method == "GET" and 'oauth_verifier' in request.GET:
		oauth_verifier = request.GET['oauth_verifier']
		#Now that you have the oauth_verifier stored to a variable, you'll want to create a new instance of Twython and grab the final user tokens
		twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

		final_step = twitter.get_authorized_tokens(oauth_verifier)
		#Once you have the final user tokens, store them in a database for later use:
		OAUTH_TOKEN = final_step['oauth_token']
		OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']


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

	auth_url = handleOAuth(request)

	return render(request, "register.html", {
		'register_form'		: register_form,
		'auth_url'			: auth_url,
		'login_form'		: LoginForm(),
		'title'				: "Register"
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

def search_twitter(request):
	twitter = handleOAuthAppOnly()
	search_result = []
	if request.method=='POST' and 'search_string' in request.POST:
		search_result = twitter.search(q=request.POST['search_string'])
		for tweet in search_result['statuses']:
		    Twython.html_for_tweet(tweet)

	return render(request, 'search_twitter.html', {
		'login_form'			: LoginForm(), 
		'search_result'			: search_result,
		'title'					: "Search Twitter"
		}, 
		context_instance=RequestContext(request))