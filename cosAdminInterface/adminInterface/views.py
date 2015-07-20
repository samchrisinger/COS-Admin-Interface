from django.shortcuts import render

def home(request):
	return render(request, 'base.html', {})

def users(request):
	return render(request, 'users.html', {})

def prereg(request):
	return render(request, 'prereg.html', {})

def analytics(request):
	return render(request, 'analytics.html', {})
