from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DirFile
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from user.serializers import DirFileDataSerializer
from user.serializers import DirFileSerializer
from user.serializers import UserSerializer
from django.contrib.auth.models import User
from django.db import transaction
import threading
import time


# Create your views here.
@login_required(login_url="/accounts/login/")
def userhome(request, username):
    if not request.user.username == username:
        return render(request, 'invalid.html')
    resdocs = DirFile.objects.filter(owner__exact=request.user.id).filter(parentId__exact="0")
    context = {'files': resdocs}
    return render(request, 'userhome.html', context)


def dfs(node, tab):
    if node.dorf == 'f':
        return " " * tab + "|\n" + " " * tab + "|___ " + node.name + "\n"
    else:
        children = DirFile.objects.filter(owner__exact=node.owner).filter(parentId__exact=node.id)
        children = [c for c in children]
        str = " " * tab + "|\n" + " " * tab + "|___ " + node.name + "\n"
        for c in children:
            str = str + dfs(c, tab + 6)
        return str


@login_required(login_url="/accounts/login/")
def treeview(request, username):
    resdocs = DirFile.objects.filter(owner__exact=request.user.id).filter(parentId__exact="0")
    resdocs = [r for r in resdocs]
    result = ""
    while not len(resdocs) == 0:
        node = resdocs.pop(0)
        cur = dfs(node, 0)
        result = result + cur
    context = {'resstring': result}
    return render(request, 'treeviewpage.html', context)


@login_required(login_url="/accounts/login/")
def dirview(request, pk, username):
    if not request.user.username == username:
        return render(request, 'invalid.html')
    curdir = DirFile.objects.filter(owner__exact=request.user.id).get(id=pk)
    if curdir.dorf == 'd':
        resdocs = DirFile.objects.filter(owner__exact=request.user.id).filter(parentId__exact=pk)
        dirname = curdir.name
        context = {'files': resdocs, 'dir': dirname}
        return render(request, 'directorypage.html', context)
    else:
        filename = curdir.name
        file_data = curdir.fileContent
        file_data = str(file_data)
        file_data = file_data[2:-1]
        file_data = 'zoETBZ3L+ixfypJUn2ut/24YPooKReRaQQmYkgeA/73t6j8CmSPOzu6LpSNz17tH'
        print(file_data)
        context = {'file_name': filename, 'filedata': file_data}
        return render(request, 'AESFileview.html', context)


@login_required(login_url="/accounts/login/")
@api_view(['GET', 'POST', 'DELETE'])
def get_user_data(request, username):
    try:
        userdata = User.objects.get(username__exact=username)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if userdata.profile.locked == True:
            # wait for thread to get over
            # if thread resets
            # return HttpResponse Busy
            # if thread ends
            return Response(status=status.HTTP_423_LOCKED)
        else:
            userdata.profile.locked = True
            # start the thread on server
            return Response(status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        userdata.profile.locked = False
        # kill thread

    if request.method == 'GET':
        serializer = UserSerializer(userdata)
        return Response(serializer.data)


@login_required(login_url="/accounts/login/")
@api_view(['GET'])
def all_observed_files(request, pth, username, format=None):
    # if not request.user.username == username:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).filter(
            pathLineage__startswith=pth)
    except DirFile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DirFileSerializer(filecontent, many=True)
        return Response(serializer.data)


@login_required(login_url="/accounts/login/")
@api_view(['GET', 'PUT', 'POST', 'DELETE'])
def file_contents(request, pth, username, format=None):
    # if not request.user.username == username:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        serializer = DirFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).get(
                pathLineage=pth)
        except DirFile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = DirFileSerializer(filecontent)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = DirFileSerializer(filecontent, data=request.data)
            if serializer.is_valid():
                serializer.save()
                transaction.commit()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).filter(
                pathLineage__startswith=pth)
            filecontent.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@login_required(login_url="/accounts/login/")
@api_view(['GET', 'PUT', 'POST', 'DELETE'])
def file_data(request, pth, username, format=None):
    if not request.data['username'] == username:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    print(pth)
    if request.method == 'POST':
        serializer = DirFileDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        print(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).get(
                pathLineage=pth)
        except DirFile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = DirFileDataSerializer(filecontent)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = DirFileDataSerializer(filecontent, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).filter(
                pathLineage__startswith=pth)
            filecontent.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

# @permission_classes((IsAuthenticatedOrReadOnly, ))
# class FileContent(generics.RetrieveUpdateDestroyAPIView):
#     queryset = DirFile.objects.all()
#     serializer_class = DirFileSerializer
#
# @permission_classes((IsAuthenticatedOrReadOnly, ))
# class FileData(generics.RetrieveUpdateDestroyAPIView):
#     queryset = DirFile.objects.all()
#     serializer_class = DirFileDataSerializer
