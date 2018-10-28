from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import DirFile


# Create your views here.
@login_required(login_url="/accounts/login/")
def userhome(request, username):
    if not request.user.username == username:
        return render(request, 'invalid.html')
    resdocs = DirFile.objects.filter(owner__exact=request.user.id).filter(parentId__exact="0")
    context = {'files': resdocs}
    return render(request, 'userhome.html', context)


@login_required(login_url="/accounts/login/")
def treeview(request):
    return HttpResponse("<h1>Tree View")


@login_required(login_url="/accounts/login/")
def dirview(request, id):
    return HttpResponse("<h3>Dir name {% request.dirfile.id %}")
