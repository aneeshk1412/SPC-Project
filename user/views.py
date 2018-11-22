from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DirFile
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from user.serializers import DirFileDataSerializer
from user.serializers import DirFileSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from django.db import transaction
import base64


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


def DES3dec (in_filename , iv, key):
    des3 = DES3.new(key, DES3.MODE_CFB, iv)
    with open(in_filename, 'rb') as in_file:
        with open(".deccrypt", 'wb') as out_file:
            while True:
                chunk = in_file.read(8192)
                if len(chunk) == 0:
                    break
                out_file.write(des3.decrypt(chunk))


def RSAdec (file):
    file_in = open(file, "rb")

    private_key = RSA.import_key(open("private.pem").read())

    enc_session_key, nonce, tag, ciphertext = \
        [file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    #print(data.decode("utf-8"))
    with open(".decryt",'wb') as f:
        f.write(data)

def AESdec (file , key ):
    file_in = open(file, "rb")
    nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    file_in.close()
    with open(".decryt",'wb') as f:
        f.write(data)


def decrypt(file_name):
    choice = file_name[-5:-2:1]
    print(choice)
    file_name = ".,temp"
    if (choice == 'aes'):
        key = hashlib.sha256(passwordt).digest()
        AESdec(file_name , key )
    elif (choice == 'rsa'):
        RSAdec(file_name)
    elif (choice == 'de3'):
        key = hashlib.md5(passwordt).digest()
        m = hashlib.sha224()
        m.update(passwordt)
        iv = m.digest()[:8]
        DES3dec(file_name , iv , key)

    else:
        print("Invalid try again")

@login_required(login_url="/accounts/login/")
def dirview(request, pk, username):
    if not request.user.username == username:
        return render(request, 'invalid.html')
    curdir = DirFile.objects.filter(owner__exact=request.user.id).get(id=pk)
    if curdir.dorf =='d' :
        resdocs = DirFile.objects.filter(owner__exact=request.user.id).filter(parentId__exact=pk)
        dirname = curdir.name
        context = {'files': resdocs, 'dir': dirname}
        return render(request, 'directorypage.html', context)
    else:
        passwordt = "abc!@123"

        file_data = curdir.fileContent
        with open (".,temp","wb") as f:
            f.write(file_data)
        filename = curdir.name
        decrypt(filename , passwordt)

        with open ("./decrpyt","rb") as f:
            file_data = f.read()

        context = { 'file_name': filename, 'file_data': file_data}
        return render(request, 'filepage.html', context)



@login_required(login_url="/accounts/login/")
@api_view(['GET'])
def all_observed_files(request, pth, username, format=None):
    # if not request.user.username == username:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).filter(pathLineage__startswith=pth)
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
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).get(pathLineage=pth)
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
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).filter(pathLineage__startswith=pth)
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
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).get(pathLineage=pth)
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
            filecontent = DirFile.objects.select_for_update().filter(owner__exact=request.data['owner']).filter(pathLineage__startswith=pth)
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
