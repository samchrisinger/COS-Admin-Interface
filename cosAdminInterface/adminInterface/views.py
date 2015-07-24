from django.shortcuts import render
from database import get_all_drafts
from django.http import HttpResponse
import json

def home(request):
	return render(request, 'base.html', {})

# def users(request):
# 	return render(request, 'users.html', {})

def prereg(request):
	return render(request, 'prereg/prereg.html', {})

def get_drafts(request):
	all_drafts = get_all_drafts()
	return HttpResponse(json.dumps(all_drafts), content_type='application/json')

# def analytics(request):
# 	return render(request, 'analytics.html', {})
