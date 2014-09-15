import random

from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils import timezone

# Meembership

class SocialNetwork(models.Model):
	name = models.CharField("Name of the network", max_length=256)
	description = models.CharField("Description of the service provided", max_length=512)
	home = models.URLField("Home URL of the service")
	
	def __unicode__(self):
		return self.name

class CollDemUserManager(BaseUserManager):

	def __init__(self, user=None):
		self.the_user = user

	def valid_user(self):
		return isinstance(self.the_user, CollDemUser)

	def get_pic(self):
		"logic to access the picture or get default one if undefined"
		if 	not self.valid_user() or None==self.the_user.pic.url:
			return '/static/images/users/default_pic.gif'
		return '/media/'+settings.MEDIA_URL+self.the_user.pic.url

	def get_stats(self):
		if 	not self.valid_user():
			return None
		stats = {}
		user_msgs = Message.objects.filter(author=self.the_user)
		stats['msg_count'] = len(user_msgs)
		rootMsgCount = len(user_msgs.filter(answer_to=None))
		stats['answer_count'] = stats['msg_count'] - rootMsgCount
		return stats

	def create_user(self, username, email, password=None):
		theuser = self.model(
				guid = random.getrandbits(63),
				username = username,
				email = self.normalize_email(email),
				date_joined = timezone.now()
			)
		if None!=password:
			theuser.set_password(password)
		theuser.save(using=self._db)

		return theuser

	def create_superuser(self, username, email, password):
		theuser = self.create_user(username, email, password)
		theuser.is_admin = True
		return theuser


class CollDemUser(AbstractBaseUser, PermissionsMixin):
	guid = models.BigIntegerField("Unique ID", primary_key=True, editable=False)
	first_name = models.CharField("First name", max_length=256, blank=True)
	last_name = models.CharField("Second name", max_length=256, blank=True)
	date_joined = models.DateTimeField("Created at", auto_now_add=True, editable=False)
	username = models.CharField("User name", max_length=64, unique=True)
	pic = models.ImageField(upload_to="profile_pics/%Y/", blank=True)
	email = models.EmailField("Email")
	network_memberships = models.ManyToManyField(SocialNetwork, through='NetworkMembership')
	connections = models.ManyToManyField('CollDemUser', verbose_name="Connections")

	#AbtractBaseUser contract  
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
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
	
