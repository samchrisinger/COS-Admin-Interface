from django.shortcuts import render
from database import get_all_drafts, get_schema, get_draft
from django.http import HttpResponse
import json
import utils

def home(request):
	return render(request, 'base.html', {})

def prereg(request):
	return render(request, 'prereg/prereg.html', {})

def prereg_form(request, draft_pk):
	draft = get_draft(draft_pk)
	#import ipdb; ipdb.set_trace()
	context = {'data': json.dumps(draft)}
	return render(request, 'prereg/edit_draft_registration.html', context)

def get_drafts(request):
	all_drafts = get_all_drafts()
	return HttpResponse(json.dumps(all_drafts), content_type='application/json')

def get_schemas(request):
	schema = get_schema()
	return HttpResponse(json.dumps(schema), content_type='application/json')
