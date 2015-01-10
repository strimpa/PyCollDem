import json
import string

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import Textarea

from CollDem.lang import lang
from CollDem.models import CollDemUser

def create_user_link_string(users):
	res = ""
	for user in users:
		if res!="":
			res += ", "
		res += ('<a href="/profile/'+str(user.guid)+'">'+user.username+"</a>")
	return res

def notification_list(user):
	notifications = []

	for message in user.my_messages.all():
		#replies to messages we replied to
		if message.answer_to != None:
			sibling_repliers = []
			new_sibling_repliers = []
			for sibling_reply in message.answer_to.answers.all():
				if sibling_reply.created_at > message.created_at and sibling_reply.author!=user:
					if sibling_reply.created_at < user.last_update:
						if not sibling_reply.author in sibling_repliers:
							sibling_repliers.append(sibling_reply.author)
					else: 
						if not sibling_reply.author in new_sibling_repliers:
							new_sibling_repliers.append(sibling_reply.author)

			notification_obj = {}
			if len(new_sibling_repliers)>0:
				notification_obj['text'] = ( lang("UPDATE_SIBLING_REPLY", create_user_link_string(new_sibling_repliers), message.answer_to.guid))
				notification_obj['new'] = True
			if len(sibling_repliers)>0:
				notification_obj['text'] = (lang("UPDATE_SIBLING_REPLY", create_user_link_string(sibling_repliers), message.answer_to.guid))
			if 'text' in notification_obj:
				notifications.append(notification_obj)

		repliers = []
		new_repliers = []
		for reply in message.answers.all():
			if reply.created_at > message.created_at and reply.author!=user:
				if reply.created_at < user.last_update:
					if not reply.author in repliers:
						repliers.append(reply.author)
				else:
					if not reply.author in new_repliers:
						new_repliers.append(reply.author)

		notification_obj = {}
		if len(new_repliers)>0:
			notification_obj['text'] = ( lang("UPDATE_REPLY", create_user_link_string(new_repliers), message.guid))
			notification_obj['new'] = True
		if len(repliers)>0:
			notification_obj['text'] = (lang("UPDATE_REPLY", create_user_link_string(repliers), message.guid))
		if 'text' in notification_obj:
			notifications.append(notification_obj)

	return notifications


def notifications(request):
	if request.user==None or not request.user.is_authenticated():
		return HttpResponse("user not authenticated", content_type='text/plain')

	notifications = notification_list(request.user)

	dataString = json.dumps(notifications)

	return HttpResponse(dataString, content_type='application/json')
