from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.

def userhome(request, username):
	return render(request, 'userhome.html')