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
        print()
    elif b==5:
        print()

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def encrypt(fname,pas):
    subprocess.run('javac BlowEncDec.java; java BlowEncDec e "$pas" $fname',shell=True)



client_changed_files=[]
client_added_files=[]
client_deleted_files=[]


def status(user, pas, userid, rootDir, enc_type, server_url):
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




def sync(user, pas, userid, rootDir, enc_type, server_url):
    client_server=input('Change files on client or server? (c or s): ')
    p = Path(rootDir)
    dirname = str(p.name)
    s = requests.Session()
    r1 = s.get(server_url+'/accounts/login/')
    csrf_tok = r1.cookies['csrftoken']
    payload = {'username': user, 'password': pas, 'csrfmiddlewaretoken': csrf_tok}
    rs = s.post(server_url+'/accounts/login/', payload)
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

            r2 = s.get(str(server_url + '/user/' + user + '/contents/' + dirname + '/' + relFile) + '.' + enc_type + 'en' + '/',
                       data={'owner': int(userid)})
            complete_path = os.path.join(rootDir, relFile)
            os.environ('complete_path_env')=complete_path
            os.environ('pas_env')=pas
            if (r2.ok):
                dicti = r2.json()
                if dicti['md5code'] != md5(encrypt(complete_path_env,pas_env)):
                    if client_server == 's':
                        encrypt(complete_path_env, pas_env)
                        with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
                            content = con.read()
                        if os.path.exists(complete_path + '.' + enc_type + 'en'):
                            os.remove(complete_path + '.' + enc_type + 'en')
                        dicti['fileContent'] = content
                        dicti['md5code'] = md5(complete_path)
                        dicti['username'] = user
                        del dicti['modifiedTime']
                        del dicti['pk']
                        print('Replacing on server ' + dirname + '/' + relFile + '/')
                        dic = {'owner': int(userid), 'username': user, 'password': pas}
                        progress_bar(str(
                            server_url + '/user/' + user + '/data/' + dirname + '.' + enc_type + 'en' + '/' + relFile) + '/',
                                     dicti, dic, 1, s)
                    else:
                        print('Replacing on client ' + dirname + '/' + relFile + '/')
                        progress_bar(complete_path,{},{},4,s)

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
                                name = str(dirlist[i]) + '.' + enc_type + 'en'
                                md5code = md5(complete_path)
                                dorf = 'f'
                                pathLineage = pat1
                                encrypt(complete_path_env, pas_env)
                                with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
                                    content = con.read()
                                if os.path.exists(complete_path + '.' + enc_type + 'en'):
                                    os.remove(complete_path + '.' + enc_type + 'en')
                                fileContent = content
                                dicti = {'owner': owner, 'parentId': int(parentid), 'name': name,
                                         'pathLineage': pathLineage,
                                         'dorf': dorf,
                                         'fileContent': fileContent, 'md5code': md5code, 'username': username}
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
                                         'dorf': dorf,
                                         'fileContent': fileContent, 'md5code': md5code, 'username': username}
                                dic = {}
                                print('Adding to server ' + pathLineage)
                                progress_bar(server_url + '/user/' + user + '/data/' + pathLineage,
                                             dicti, dic, 0, s)
                            else:
                                print('Deleting from client ' + pat + str(dirlist[i]) + '/')
                                progress_bar(os.path.join(rootDir, pat2), {}, {}, 3, s)
                                break

    r = s.get(url=server_url + '/user/' + user + '/allfiles/'+str(p.name), data={'owner': int(userid)})
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
                    progress_bar(server_url + '/user/' + user + '/data/' + fil[0:-7] + '/', dicti, dic, 2, s)
                else:
                    print('Deleting from server ' + fil)
                    progress_bar(server_url + '/user/' + user + '/data/' + fil, dicti, dic, 2, s)
            else:
                print()
