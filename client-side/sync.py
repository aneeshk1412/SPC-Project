import base64
import hashlib
import os
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta
import time
import progressbar
import threading
import subprocess
import pythonencryptAES



def progress_bar(ur,dat,dat1,b,s):
    widgets = [progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()]
    pbar = progressbar.ProgressBar(widgets=widgets)
    thread = threading.Thread(target=delete_post,
                              args=(ur,dat,dat1,b,s,))
    thread.daemon = True
    thread.start()
    pbar.start()
    i = 1
    while True:
        time.sleep(0.1)
        pbar.update(i)
        if not thread.is_alive():
            pbar.finish()
            break
        i += 1

def delete_post(ur, dat,dat1,b,s):
    if b==0:
        s.post(url=ur,data=dat)
    elif b==1:
        s.delete(url=ur,data=dat1)
        s.post(url=ur, data=dat)
    elif b==2:
        s.delete(url=ur,data=dat1)
    elif b==3:
        if os.path.exists(ur):
            os.remove(ur)
    elif b==4:
        if os.path.exists(ur):
            os.remove(ur)
        decrypt(ur,s,dat,dat1)
    elif b==5:
        l = len(ur)
        decrypt(ur,s, dat, dat1)
        # else:
        #     if not os.path.exists(ur):
        #         os.makedirs(ur)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def encrypt(fname,enc_pas,enc_type):
    if enc_type=='blo':
        subprocess.call("javac BlowEncDec.java")
        subprocess.call("java BlowEncDec e"  + fname+ enc_pas)
    elif enc_type=='aes':
        pythonencryptAES.encrypt(fname,enc_pas)



def decrypt(fname,fcontent,enc_pas,enc_type):
    if enc_type=='blo':
        subprocess.call("javac BlowEncDec.java")
        subprocess.call("java BlowEncDec e"  + fname+fcontent+ enc_pas)
    elif enc_type=='aes':
        pythonencryptAES.decrypt(fname,fcontent,enc_pas)




client_changed_files=[]
client_added_files=[]
client_deleted_files=[]


def status(user, pas, userid, rootDir, enc_type, enc_pas, server_url):
    p = Path(rootDir)
    dirname = str(p.name)
    s = requests.Session()
    r1 = s.get(server_url + '/accounts/login/')
    csrf_tok = r1.cookies['csrftoken']
    payload = {'username': user, 'password': pas, 'csrfmiddlewaretoken': csrf_tok}
    rs = s.post(server_url + '/accounts/login/', payload)
    file_dir_list=[]
    for dir_, _, files in os.walk(rootDir):
        relDir1 = os.path.relpath(dir_, rootDir)
        if relDir1[0:1] == ".":
            file_dir_list.append(dirname + '/')
        else:
            file_dir_list.append(dirname + '/' + relDir1 + '/')
        for fileName in files:
            relDir = os.path.relpath(dir_, rootDir)
            relFile = os.path.join(relDir, fileName)
            if relFile[0:2] == "./":
                relFile = relFile[2:]
            file_dir_list.append(dirname + '/' + relFile + '.' + enc_type + 'en' + '/')

            r2 = s.get(str(server_url+'/user/' + user + '/contents/' + dirname + '/' + relFile) + '.' + enc_type + 'en' + '/', data={'owner': int(userid)})
            complete_path = os.path.join(rootDir, relFile)
            if (r2.ok):
                dicti = r2.json()
                if dicti['md5code'] != md5(complete_path):
                    client_changed_files.append(str(dirname+'/'+relFile+'/'))
            else:
                dirlist = os.path.normpath(dirname + '/' + relFile)
                dirlist = dirlist.split(os.sep)
                for i in range(len(dirlist)):
                    pat=''
                    if i==len(dirlist)-1:
                        for j in range(i):
                            pat = pat + str(dirlist[j]) + '/'
                        pat = pat + str(dirlist[i]) +'.'+enc_type+'en'+ '/'
                        r2 = s.get(server_url + '/user/' + user + '/contents/' + pat, data={'owner': int(userid)})
                        if not r2.ok:
                            client_added_files.append(pat[0:-7]+'/')
                    else:
                        for j in range(i + 1):
                            pat = pat + str(dirlist[j]) + '/'
                        r2 = s.get(server_url + '/user/' + user + '/contents/' + pat, data={'owner': int(userid)})
                        if not r2.ok:
                            client_added_files.append(pat)

    r = s.get(url=server_url + '/user/' + user + '/allfiles/' + dirname, data={'owner': int(userid)})
    dat = r.json()
    for pat in dat:
        fil=pat['pathLineage']
        if not fil in file_dir_list:
            l=len(fil)
            if fil[l-7:l-1]==str('.'+enc_type+'en'):
                client_deleted_files.append(fil[0:-7]+'/')
            else:
                client_deleted_files.append(fil)
    print('Files different in client and server: ',end='')
    print(client_changed_files)
    print('Files in client and not in server: ', end='')
    print(client_added_files)
    print('Files not in client and in server: ', end='')
    print(client_deleted_files)




def sync(user, pas, userid, rootDir, enc_type, enc_pas, server_url):

    p = Path(rootDir)
    dirname = str(p.name)
    s = requests.Session()
    r1 = s.get(server_url+'/accounts/login/')
    csrf_tok = r1.cookies['csrftoken']
    payload = {'username': user, 'password': pas, 'csrfmiddlewaretoken': csrf_tok}
    rs = s.post(server_url+'/accounts/login/', payload)
    # r = s.get(url=server_url + '/user/' + user + '/allfiles/' + str(p.name), data={'owner': int(userid)})
    # dat = r.json()
    # enc_ty=''
    # for pat in dat:
    #     enc_ty=pat['encryption_scheme']
    #     break
    # if enc_ty==enc_type:
    #     client_server = input('Change files on client or server? (c or s): ')
    # else:
    #     g = open(os.path.expanduser(os.path.join("~", "spc_details/enc.txt")), "w+")
    #     g.write(enc_type + '\n')
    #     g.write(enc_pas + '\n')
    #     g.close()
    client_server = input('Change files on client or server? (c or s): ')

    file_dir_list = []
    for dir_, _, files in os.walk(rootDir):
        relDir1 = os.path.relpath(dir_, rootDir)
        if relDir1[0:1] == ".":
            file_dir_list.append(dirname + '/')
        else:
            file_dir_list.append(dirname + '/' + relDir1 + '/')
        for fileName in files:
            relDir = os.path.relpath(dir_, rootDir)
            relFile = os.path.join(relDir, fileName)
            if relFile[0:2] == "./":
                relFile = relFile[2:]
            file_dir_list.append(dirname + '/' + str(relFile) + '.' + enc_type + 'en' + '/')
            # print(str(server_url + '/user/' + user + '/contents/' + dirname + '/' + relFile) + '.' + enc_type + 'en' + '/')
            r2 = s.get(str(server_url + '/user/' + user + '/contents/' + dirname + '/' + relFile) + '.' + enc_type + 'en' + '/',
                       data={'owner': int(userid)})
            complete_path = os.path.join(rootDir, relFile)
            if (r2.ok):
                dicti = r2.json()

                md=md5(complete_path)
                if dicti['md5code'] != md:
                    if client_server == 's':
                        encrypt(complete_path, enc_pas, enc_type)
                        with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
                            content = con.read()
                        if os.path.exists(complete_path + '.' + enc_type + 'en'):
                            os.remove(complete_path + '.' + enc_type + 'en')
                        content=str(content.decode())
                        #content=content[2:-1]
                        dicti['fileContent'] = content
                        dicti['md5code'] = md
                        dicti['username'] = user
                        dicti['encryption_scheme']=enc_type
                        del dicti['modifiedTime']
                        del dicti['pk']
                        # print(dicti)
                        print('Replacing on server ' + dirname + '/' + relFile + '/')
                        dic = {'owner': int(userid), 'username': user, 'password': pas}
                        # print(str(
                        #     server_url + '/user/' + user + '/data/' + dirname +  '/' +'.' + enc_type + 'en' + relFile) + '/')
                        progress_bar(str(
                            server_url + '/user/' + user + '/data/' + dirname + '/'  + relFile) + '.' + enc_type + 'en'+ '/',
                                     dicti, dic, 1, s)
                    else:
                        r2 = s.get(str(server_url + '/user/' + user + '/data/' + dirname + '/' + relFile) + '.' + enc_type + 'en'+'/',
                                   data={'owner': int(userid), 'username': user, 'password': pas})
                        dat=r2.json()
                        content=str(dat['fileContent']).encode()
                        print('Replacing on client ' + dirname + '/' + relFile + '/')
                        progress_bar(complete_path,enc_pas,enc_type,4,content)
            else:
                dirlist = os.path.normpath(dirname + '/' + relFile)
                dirlist = dirlist.split(os.sep)
                for i in range(len(dirlist)):
                    pat = ''
                    if i == len(dirlist) - 1:
                        for j in range(i):
                            pat = pat + str(dirlist[j]) + '/'
                        pat1 = pat + str(dirlist[i]) + '.' + enc_type + 'en' + '/'
                        r2 = s.get(server_url + '/user/' + user + '/contents/' + pat1, data={'owner': int(userid)})
                        if not r2.ok:
                            if client_server == 's':
                                r3 = s.get(server_url + '/user/' + user + '/contents/' + pat,
                                           data={'owner': int(userid)})
                                data2 = r3.json()
                                parentid = data2['pk']
                                owner = int(userid)
                                username = user
                                file_type =str(dirlist[i])[-3:]
                                name = str(dirlist[i]) + '.' + enc_type + 'en'
                                encrypt(complete_path, enc_pas, enc_type)

                                md5code = md5(complete_path)
                                dorf = 'f'
                                pathLineage = pat1
                                with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
                                    content = con.read()
                                if os.path.exists(complete_path + '.' + enc_type + 'en'):
                                    os.remove(complete_path + '.' + enc_type + 'en')
                                fileContent = str(content.decode())
                                #fileContent = fileContent[2:-1]
                                print(fileContent)
                                dicti = {'owner': owner, 'parentId': int(parentid), 'name': name,
                                         'pathLineage': pathLineage,
                                         'dorf': dorf,
                                         'fileContent': fileContent, 'md5code': md5code, 'username': username,
                                         'encryption_scheme': enc_type, 'file_type': file_type }
                                # print(dicti)
                                dic = {}
                                print('Adding to server ' + pathLineage)
                                progress_bar(server_url + '/user/' + user + '/data/' + pathLineage,
                                             dicti, dic, 0, s)
                            else:
                                print('Deleting from client ' + pat + str(dirlist[i]) + '/' )
                                progress_bar(complete_path,{},{},3,s)
                    else:
                        pat2=''
                        for j in range(i):
                            pat2=pat2+str(dirlist[j+1]) + '/'
                            pat = pat + str(dirlist[j]) + '/'
                        pat1 = pat + str(dirlist[i]) + '/'
                        r2 = s.get(server_url + '/user/' + user + '/contents/' + pat1, data={'owner': int(userid)})
                        if not r2.ok:
                            if client_server == 's':
                                r3 = s.get(server_url + '/user/' + user + '/contents/' + pat,
                                           data={'owner': int(userid)})
                                if r3.ok:
                                    data2 = r3.json()
                                    parentid = data2['pk']
                                else:
                                    parentid = 0

                                owner = int(userid)
                                username = user
                                name = str(dirlist[i])
                                md5code = '-'
                                dorf = 'd'
                                pathLineage = pat + str(name) + '/'
                                fileContent = '-'
                                dicti = {'owner': owner, 'parentId': int(parentid), 'name': name,
                                         'pathLineage': pathLineage,
                                         'dorf': dorf, 'encryption_scheme':enc_type,'file_type':'-',
                                         'fileContent': fileContent, 'md5code': md5code, 'username': username}
                                dic = {}
                                print('Adding to server ' + pathLineage)
                                progress_bar(server_url + '/user/' + user + '/data/' + pathLineage,
                                             dicti, dic, 0, s)
                            else:
                                print('Deleting from client ' + pat + str(dirlist[i]) + '/')
                                progress_bar(os.path.join(rootDir, pat2), {}, {}, 3, s)
                                break

    r = s.get(url=server_url + '/user/' + user + '/allfiles/' + str(p.name), data={'owner': int(userid)})
    dat=r.json()
    for pat in dat:
        fil=pat['pathLineage']
        if not fil in file_dir_list:
            if client_server == 's':
                dic = {'owner': int(userid), 'username': user, 'password': pas}
                dicti = {}
                l = len(fil)
                if fil[l - 7:l - 1] == str('.' + enc_type + 'en'):
                    print('Deleting from server ' + fil[0:-7] + '/')
                    progress_bar(server_url + '/user/' + user + '/data/' + fil , dicti, dic, 2, s)
                else:
                    print('Deleting from server ' + fil)
                    progress_bar(server_url + '/user/' + user + '/data/' + fil, dicti, dic, 2, s)
            else:
                r5=s.get(server_url + '/user/' + user + '/data/' + fil,data={'owner': int(userid), 'username': user, 'password': pas})
                dat5=r5.json()
                content=str(dat5['fileContent']).encode()
                dirlist = os.path.normpath(fil)
                dirlist = dirlist.split(os.sep)
                fil_pat=''
                for i in range(len(dirlist)-1):
                    fil_pat=fil_pat+str(dirlist[i+1]) +'/'
                print('Adding to client ' + fil[:-7]+'/')
                patn=os.path.join(rootDir, fil_pat)
                progress_bar(patn[:-7],enc_pas,enc_type,5,content)
