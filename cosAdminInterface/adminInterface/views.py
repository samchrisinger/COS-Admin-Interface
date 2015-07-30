from django.shortcuts import render
from database import get_all_drafts, get_schema
from django.http import HttpResponse
import json

def home(request):
	return render(request, 'base.html', {})

def prereg(request):
	return render(request, 'prereg/prereg.html', {})

def get_drafts(request):
	all_drafts = get_all_drafts()
	return HttpResponse(json.dumps(all_drafts), content_type='application/json')

def get_schemas(request):
	schema = get_schema()
	return HttpResponse(json.dumps(schema), content_type='application/json')
