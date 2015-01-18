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

#Helper functions

def create_user_link_string(users):
	res = ""
	for user in users:
		if res!="":
			res += ", "
		if user != None:
			res += ('<a href="/profile/'+str(user.guid)+'">'+user.username+"</a>")
		else:
			res += ('An anonymous user')
	return res

def searchMessages(notifications, message, answer_to, user, answers, notification_text):
	repliers = []
	new_repliers = []
	for reply in answers:
		if reply.created_at > message.created_at and reply.author!=user:
			if reply.created_at < user.last_update:
				if not reply.author in repliers:
					repliers.append(reply.author)
			else: 
				if not reply.author in new_repliers:
					new_repliers.append(reply.author)

	notification_obj = {}
	if len(new_repliers)>0:
		notification_obj['text'] = ( lang(notification_text, create_user_link_string(new_repliers), answer_to.guid))
		notification_obj['new'] = True
	if len(repliers)>0:
		notification_obj['text'] = (lang(notification_text, create_user_link_string(repliers), answer_to.guid))
	if 'text' in notification_obj:
		notifications.append(notification_obj)

def searchEvaluations(notifications, message, user, notification_text):
	evaluators = []
	new_evaluators = []
	for evaluation in message.user_evaluation.all():
		evaluator = evaluation.evaluator
		if evaluation.updated_at > message.created_at and evaluator!=user:
			if evaluation.updated_at < user.last_update:
				if not evaluator in evaluators:
					evaluators.append(evaluator)
			else: 
				if not evaluator in new_evaluators:
					new_evaluators.append(evaluator)

	notification_obj = {}
	if len(new_evaluators)>0:
		notification_obj['text'] = ( lang(notification_text, create_user_link_string(new_evaluators), message.guid))
		notification_obj['new'] = True
	if len(evaluators)>0:
		notification_obj['text'] = (lang(notification_text, create_user_link_string(evaluators), message.guid))
	if 'text' in notification_obj:
		notifications.append(notification_obj)

#controller functions

def notification_list(user):
	notifications = []

	for message in user.my_messages.all():
		#replies to messages we replied to
		if message.answer_to != None:
			searchMessages(notifications, message, message.answer_to, user, message.answer_to.answers.all(), 'UPDATE_SIBLING_REPLY')

		searchMessages(notifications, message, message, user, message.answers.all(), 'UPDATE_REPLY')
		searchEvaluations(notifications, message, user, 'UPDATE_EVALLUATION')
	return notifications


def notifications(request):
	if request.user==None or not request.user.is_authenticated():
		return HttpResponse("user not authenticated", content_type='text/plain')

	notifications = notification_list(request.user)

	dataString = json.dumps(notifications)

	return HttpResponse(dataString, content_type='application/json')
