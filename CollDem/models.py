from django.db import models

# Meembership

class SocialNetwork(models.Model):
	name = models.CharField("Name of the network", max_length=256)
	description = models.CharField("Description of the service provided", max_length=512)
	home = models.URLField("Home URL of the service")
	
	def __unicode__(self):
		return self.name

class User(models.Model):
	firstName = models.CharField("First name", max_length=256)
	secondName = models.CharField("Second name", max_length=256)
	nickName = models.CharField("User name", max_length=256)
	email = models.EmailField("Email")
	networkMemberships = models.ManyToManyField(SocialNetwork, through='NetworkMembership')
	connections = models.ManyToManyField('User', verbose_name="Connections")

	def __unicode__(self):
		return self.firstName + " " + self.secondName
	
class NetworkMembership(models.Model):
	network = models.ForeignKey(SocialNetwork, verbose_name="The network we are a member of")
	user = models.ForeignKey(User, verbose_name="Who is the member")
	username = models.CharField("The foreign network's user identifier", max_length=32)
	userLink = models.URLField("An optional link to the user data")

	def __unicode__(self):
		return self.username + "@" + self.network.name

class Visibility(models.Model):
	VISIBILITY_CHOICES = (
		('CONNECTIONS', 'All connections'),
		('NETWORK', 'A certain network'),
		('USERS', 'Certain users')
	)
	visibility = models.CharField("The selected visibility mode", max_length=16, choices=VISIBILITY_CHOICES)
	users = models.ManyToManyField(User, verbose_name="Manually selected users")

class Message(models.Model):
	#content
	createdAt = models.DateField("Created at")
	user = models.ForeignKey(User, verbose_name="Creator of this message")
	header = models.CharField("Header", max_length="256")
	text = models.CharField("The content", max_length=1024)
	visibility = models.OneToOneField(Visibility, verbose_name='Message visibility')
	#answer content
	textSelection = models.PositiveIntegerField("A text position anchor in a message this message answers to.")
	answerTo = models.ForeignKey('Message', verbose_name="The message this is an answer to.")
	
	def __unicode__(self):
		return self.header
	
