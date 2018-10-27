from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib.auth import login, logout

def homepage(request):
    return render(request,'homepage.html')
    #return HttpResponse('homepage')

def logout_view(request):
	return HttpResponse('logout')

def login_view(request):
	return HttpResponse('login')

def signup_view(request):
	return HttpResponse('signup')
