from database import get_all_drafts, get_schema, get_draft
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, logout as logout_user, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django.http import HttpResponse
import json
import utils

from adminInterface.forms import RegistrationForm, LoginForm
from adminInterface.models import AdminUser
import logging

def is_in_prereg_group(user):
	return user.groups.filter(name='prereg_group').exists()

def is_in_general_administrator_group(user):
	return user.groups.filter(name='general_administrator_group').exists()

@login_required
def home(request):
	context = {'user': request.user}
	return render(request, 'home.html', context)

def register(request):
	if request.user.is_authenticated():
		return redirect('/')
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			user = User.objects.create_user(username=username,
				email=email, password=password)
			user.save()
			admin_user = AdminUser(user=user)
			admin_user.save()
			admin_user = authenticate(username=username, password=password)
			auth_login(request, admin_user)
			return redirect('/')
		else:
			context = {'form': form}
			return render(request, 'register.html', context)
	else:
		''' User not submitting form, show blank registrations form '''
		form = RegistrationForm()
		context = {'form': form}
		return render(request, 'register.html', context)

def login(request):
	if request.user.is_authenticated():
		return redirect('/')
	form = LoginForm(request.POST or None)
	if request.POST and form.is_valid():
		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password')
		admin_user = authenticate(username=username, password=password)
		if admin_user:
			auth_login(request, admin_user)
			return redirect('/')
		else:
			return redirect('/login/')
	context = {'form': form}
	return render(request, 'login.html', context)

def logout(request):
	logout_user(request)
	return redirect('/login/')

@login_required
@user_passes_test(is_in_general_administrator_group)
def users(request):
	context = {}
	return render(request, 'users.html', context)

@login_required
@user_passes_test(is_in_prereg_group)
def prereg(request):
	context = {'user': request.user}
	return render(request, 'prereg/prereg.html', context)

@login_required
def prereg_form(request, draft_pk):
	draft = get_draft(draft_pk)
	#import ipdb; ipdb.set_trace()
	context = {'data': json.dumps(draft)}
	return render(request, 'prereg/edit_draft_registration.html', context)

@login_required
def get_drafts(request):
	all_drafts = get_all_drafts()
	return HttpResponse(json.dumps(all_drafts), content_type='application/json')

@login_required
def get_schemas(request):
	schema = get_schema()
	return HttpResponse(json.dumps(schema), content_type='application/json')
