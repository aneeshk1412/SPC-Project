from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect


# Create your views here.

def userhome(request, username):
    return render(request, 'userhome.html')


def treeview(request):
    return HttpResponse("<h1>Tree View")


def dirview(request, id):
    return HttpResponse("<h3>Dir name {% request.dirfile.id %}")
