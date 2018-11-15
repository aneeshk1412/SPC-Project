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


def dfs(node,tab):
    if node.dorf == 'f':
        return " "*tab + "|\n" + " "*tab + "|___ "+node.name+"\n"
    else:
        children = DirFile.objects.filter(owner__exact=node.owner).filter(parentId__exact=node.id)
        children = [c for c in children]
        str = " "*tab + "|\n" + " "*tab + "|___ "+node.name+"\n"
        for c in children:
            str = str + dfs(c,tab+6)
        return str


@login_required(login_url="/accounts/login/")
def treeview(request,username):
    resdocs = DirFile.objects.filter(owner__exact=request.user.id).filter(parentId__exact="0")
    resdocs = [r for r in resdocs]
    result = ""
    while not len(resdocs)==0:
        node = resdocs.pop(0)
        cur = dfs(node,0)
        result = result + cur
    print(result)
    return HttpResponse("<h3>"+result)


@login_required(login_url="/accounts/login/")
def dirview(request, pk, username):
    if not request.user.username == username:
        return render(request, 'invalid.html')
    resdocs = DirFile.objects.filter(owner__exact=request.user.id).filter(parentId__exact=pk)
    dirname = DirFile.objects.get(id=pk)
    context = {'files': resdocs, 'dir': dirname}
    return render(request, 'directorypage.html', context)
