from django.shortcuts import render
from database import get_all_drafts
from django.http import HttpResponse

def home(request):
	return render(request, 'base.html', {})

# def users(request):
# 	return render(request, 'users.html', {})

def prereg(request):
	return render(request, 'prereg/prereg.html', {})

def get_drafts(request):
	all_drafts = get_all_drafts()
	return HttpResponse(all_drafts)

# def analytics(request):
# 	return render(request, 'analytics.html', {})
