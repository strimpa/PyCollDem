import random
import datetime

from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import django_facebook

# Meembership

class SocialNetwork(models.Model):
	name = models.CharField("Name of the network", max_length=256)
	description = models.CharField("Description of the service provided", max_length=512)
	home = models.URLField("Home URL of the service")
	
	def __unicode__(self):
		return self.name

class CollDemUserManager(BaseUserManager):

	def set_user(self, user):
		self.the_user = user

	def valid_user(self):
		return isinstance(self.the_user, CollDemUser)

	def get_pic(self, user=None):
		"logic to access the picture or get default one if undefined"
		if None!=user:
			self.set_user(user)
		if 	not self.valid_user() or \
			not self.the_user.pic or \
			None==self.the_user.pic.url:
			return settings.MEDIA_URL+'/profile_pics/default_pic.gif'
		return self.the_user.pic.url

	def get_stats(self):
		if 	not self.valid_user():
			return None
		stats = {}
		user_msgs = Message.objects.filter(author=self.the_user)
		stats['msg_count'] = len(user_msgs)
		rootMsgCount = len(user_msgs.filter(answer_to=None))
		stats['answer_count'] = stats['msg_count'] - rootMsgCount
		return stats

	def get_unique_id(self):
		guid = random.getrandbits(60)
		return guid
		while(True):
			try:
				CollDemUser.objects.get(guid=guid)
				guid = random.getrandbits(63)
				#go on with while loop until exception is raised that no user exists
			except ObjectDoesNotExist:
				return guid

	def create_user(self, username, email, password=None):
		the_id = self.get_unique_id()
		theuser = self.model(
				guid = the_id,
				username = username,
				email = self.normalize_email(email)
		)
		if None!=password:
			theuser.set_password(password)
		theuser.save(using=self._db)

		return theuser

	def create_superuser(self, username, email, password):
		theuser = self.create_user(username, email, password)
		theuser.is_admin = True
		theuser.is_active = True
		return theuser


class CollDemUser(AbstractBaseUser, PermissionsMixin, django_facebook.models.BaseFacebookModel):
	guid = models.BigIntegerField("Unique ID", primary_key=True, editable=False)
	first_name = models.CharField("First name", max_length=256, blank=True)
	last_name = models.CharField("Second name", max_length=256, blank=True)
	date_joined = models.DateField("Created at", auto_now_add=True, editable=False)
	username = models.CharField("User name", max_length=64, unique=True)
	pic = models.ImageField(upload_to="profile_pics/%Y/", blank=True)
	email = models.EmailField("Email")
	network_memberships = models.ManyToManyField(SocialNetwork, through='NetworkMembership')
	connections = models.ManyToManyField('CollDemUser', verbose_name="Connections")

	#AbtractBaseUser contract  
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)

	objects = CollDemUserManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']

	def __unicode__(self):
		return self.first_name + " " + self.last_name

	def get_full_name():
		return self.first_name + " " + self.last_name

	def get_short_name():
		return self.username

	
class NetworkMembership(models.Model):
	network = models.ForeignKey(SocialNetwork, verbose_name="The network we are a member of")
	member = models.ForeignKey(CollDemUser, verbose_name="Who is the member")
	username = models.CharField("The foreign network's user identifier", max_length=32)
	user_link = models.URLField("An optional link to the user data")

	def __unicode__(self):
		return self.username + "@" + self.network.name

class Message(models.Model):
	#constants
	VISIBILITY_CHOICES = (
		('PUBLIC', 'Everyone'),
		('CONNECTIONS', 'All connections'),
		('NETWORK', 'A certain network'),
		('USERS', 'Certain users')
	)
	#content
	guid = models.CharField("Unique short description string in url escaped format.", max_length=128, primary_key=True)
	created_at = models.DateTimeField("Created at", auto_now_add=True)
	author = models.ForeignKey(CollDemUser, verbose_name="Creator of this message", null=True, related_name="my_messages")
	header = models.CharField("Header", max_length="256")
	text = models.TextField("The content", max_length=1024)
	visibility = models.CharField("The selected visibility mode", max_length=16, choices=VISIBILITY_CHOICES)
	visible_to_users = models.ManyToManyField(CollDemUser, verbose_name="Manually selected users", related_name="visible_messages")
	#answer content
	text_selection = models.PositiveIntegerField("A text position anchor in a message this message answers to.", null=True)
	answer_to = models.ForeignKey('Message', verbose_name="The message this is an answer to.", related_name="answers", null=True)
	
	def __unicode__(self):
		return self.header

class KeywordList(models.Model):
	for_msg = models.OneToOneField(Message, verbose_name="The message for which these keyworkds are created")

class Keyword(models.Model):
	name = models.CharField("Keyword", max_length="128", primary_key=True)
	keywordset = models.ManyToManyField(KeywordList)

class EvaluationSet(models.Model):
	evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="The user giving the evaluation.", related_name="my_evaluations")
	target_msg = models.ForeignKey(Message, verbose_name="The evaluated message.", related_name="user_evaluation")
	comment = models.OneToOneField(Message, verbose_name="The answer message commenting the evaluation.", related_name="commented_evaluation", null=True)

	def __unicode__(self):
		returnString = "Evaluation\nEvaluator:"+evaluator.username
		for e in evaluation_set:
			returnString += "\t"+e.name+":"+str(e.factor)
		return 


class Evaluation(models.Model):
	"A tuple pair for a user evaluation"

	EVAL_DEFAULT_CHOICES = (
		('HELPFUL', 'helpful'),
		('FUNNY', 'funny'),
		('INSPIRATIONAL', 'inspirational'),
	)

	name = models.CharField("Descriptor or the evaluation", max_length="64", choices=EVAL_DEFAULT_CHOICES)
	factor = models.FloatField("The evaluation value")
	evaluation_set = models.ForeignKey(EvaluationSet)

	def __unicode__(self):
		return (name+":"+str(factor))

