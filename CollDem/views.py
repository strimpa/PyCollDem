from django.shortcuts import render
from CollDem.forms import LogOnForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.http import HttpResponse

def home(request):
	logon_form = LogOnForm()
	entermsg_form
	user = AnonymousUser()

	if request.method=='POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(request, user)
		else:
			logon_form = LogOnForm(data=request.POST)

	return render(request, 'home.html', {'logon_form':logon_form, 'user':user}, context_instance=RequestContext(request))
