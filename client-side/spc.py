#!/usr/bin/env python3

# imports
import sys
import getpass
import os.path
import requests
import subprocess
import sync

# Global variables for logging in
s = requests.Session()
r1 = s.get('http://127.0.0.1:8000/accounts/login/')
csrf_tok = r1.cookies['csrftoken']
payload = {'username' : '', 'password' : '', 'csrfmiddlewaretoken' : csrf_tok }

if not os.path.exists(os.path.expanduser(os.path.join("~", "spc_details"))):
    os.makedirs(os.path.expanduser(os.path.join("~", "spc_details")))  # dir for storing details

# Functions for performing operations
def logintosite(user, pas):
    payload['username'] = user
    payload['password'] = pas
    r2 = s.post('http://127.0.0.1:8000/accounts/login/', payload)
    return r2.ok

def makeuser(user, pas, enc_type):
    f = open(os.path.expanduser(os.path.join("~", "spc_details/auth.txt")), "w+")
    f.write(user+'\n')
    f.write(pas+'\n')
    f.close()
    g=open(os.path.expanduser(os.path.join("~", "spc_details/enc.txt")), "w+")
    g.write(enc_type)
    g.close()

def observer_dir(dir):
    f = open(os.path.expanduser(os.path.join("~", "spc_details/dir.txt")), "w+")
    f.write(dir)
    f.close()

def set_url(ur):
    f = open(os.path.expanduser(os.path.join("~", "spc_details/ur.txt")), "w+")
    f.write(ur)
    f.close()


# Conditions required for arguments
login_cond = len(sys.argv)==3 and sys.argv[1]=="config" and sys.argv[2]=="edit"
observe_path_cond = len(sys.argv)==3 and sys.argv[1]=="observe"
sync_dir_cond = len(sys.argv)==2 and sys.argv[1]=="sync"
set_url_cond= len(sys.argv)==4 and sys.argv[1]=='server' and sys.argv[2]=='set-url'
server_cond=len(sys.argv)==2 and sys.argv[1]=='server'

# Operations to perform for the conditions

if login_cond:
    user=input('Username: ')
    pas=getpass.getpass(prompt='Password: ', stream=None)
    cpas=getpass.getpass(prompt='Confirm Password: ', stream=None)
    enc_type=input('Encryption Type (des or aes or rsa): ')
    if pas==cpas:
        if logintosite(user,pas):
            print('Login as '+user+' was successful')
            makeuser(user,pas,enc_type)
        else:
            print('Login was unsuccessful.. please check credentials or network again')
    else:
        print('The passwords did not match, please try again')
elif observe_path_cond:
    observer_dir(sys.argv[2])
elif set_url_cond:
    set_url(sys.argv[3])
elif sync_dir_cond:
    a=0
    b=0
    c=0
    d=0
    usr=''
    pa=''
    root_dir=''
    server_url=''
    if os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/auth.txt"))):
        f = open(os.path.expanduser(os.path.join("~", "spc_details/auth.txt")))
        con = f.readlines()
        usr = con[0].strip()
        pa = con[1].strip()
        f.close()
        a=1
    else:
        user = input('Username: ')
        pas = getpass.getpass(prompt='Password: ', stream=None)
        cpas = getpass.getpass(prompt='Confirm Password: ', stream=None)
        if pas == cpas:
            if logintosite(user, pas):
                print('Login as ' + user + ' was successful')
                usr=user
                pa=pas
                a=1
            else:
                print('Login was unsuccessful.. please check credentials or network again')
        else:
            print('The passwords did not match, please try again')
    if os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/enc.txt"))):
        f = open(os.path.expanduser(os.path.join("~", "spc_details/enc.txt")))
        enc_type = f.readline()
        f.close()
        b=1
    else:
        enc_type = input('Encryption Type (des or aes or rsa): ')
        g = open(os.path.expanduser(os.path.join("~", "spc_details/enc.txt")), "w+")
        g.write(enc_type)
        g.close()
        b=1
    if os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/dir.txt"))):
        f = open(os.path.expanduser(os.path.join("~", "spc_details/dir.txt")))
        root_dir = f.readline()
        f.close()
        c=1
    else:
        print('Error: spc observe <dir> command needs to be run before running sync')

    if os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/ur.txt"))):
        f = open(os.path.expanduser(os.path.join("~", "spc_details/ur.txt")))
        server_url = f.readline()
        f.close()
        d=1
    else:
        print('Error: spc server set-url <url> command needs to be run before running sync')
    user_id = 1
    if a==1 and b==1 and c==1 and d==1:
        sync.sync(usr, pa, user_id, root_dir, enc_type, server_url)
elif server_cond:
    if os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/ur.txt"))):
        f = open(os.path.expanduser(os.path.join("~", "spc_details/ur.txt")))
        server_url = f.readline()
        f.close()
        #ip and port
    else:
        print('Error: spc server set-url <url> command needs to be run to know server ip and port')

