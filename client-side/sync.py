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
import encrypt



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

def md5(fname):
	hash_md5 = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()



def sync(user, pas, userid, rootDir, enc_type, server_url):
	p = Path(rootDir)
	s = requests.Session()
	r1 = s.get(server_url+'/accounts/login/')
	csrf_tok = r1.cookies['csrftoken']
	payload = {'username': user, 'password': pas, 'csrfmiddlewaretoken': csrf_tok}
	rs = s.post(server_url+'/accounts/login/', payload)
	file_dir_list = []
	for dir_, _, files in os.walk(rootDir):
		relDir1 = os.path.relpath(dir_, rootDir)
		if relDir1[0:1] == ".":
			file_dir_list.append(str(p.name) + '/')
		else:
			file_dir_list.append(str(p.name) + '/' + relDir1 + '/')

		for fileName in files:
			relDir = os.path.relpath(dir_, rootDir)
			relFile = os.path.join(relDir, fileName)

			if relFile[0:2] == "./":
				relFile = relFile[2:]
			file_dir_list.append(  str(p.name)+ '/' +relFile+'/')
			dirname = str(p.name)
			st = str(server_url+'/user/' + user + '/contents/' + dirname + '/' + relFile) + '/'

			r2 = s.get(st, data={'owner': int(userid)})
			complete_path = os.path.join(rootDir, relFile)
			if (r2.ok):
				dicti = r2.json()
				if dicti['md5code'] != md5(complete_path):
					with open(complete_path,'rb') as inp:
						with open('outfile','wb') as out:
							base64.encode(inp,out)
					with open('outfile','rb') as con:
						content=con.readlines()
					# encrypt.encrypt(complete_path, enc_type,pas)
					# with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
					# 	content = con.read()
					# if os.path.exists(complete_path + '.' + enc_type + 'en'):
					# 	os.remove(complete_path + '.' + enc_type + 'en')
					# if(dicti['modifiedTime'] > datetime.fromtimestamp(os.stat(complete_path).st_mtime)):
					# 	ans=input('Do u want to modify this file? Y or N')
					# 	if(ans=='Y'):
					r2=s.get( str(server_url+'/user/' + user + '/data/' + dirname + '/' + relFile) + '/', data={'owner': int(userid),'username':user,'password':pas})
					dictic=r2.json()
					dictic['fileContent']=content
					dictic['md5code']= md5(complete_path)
					dictic['username']=user
					del dictic['modifiedTime']
					del dictic['pk']
					# print(type(content))
					# print(str(server_url+'/user/' + user + '/data/' + str(p.name) + '/' + relFile) + '/')
					print('Replacing ' + str(p.name) + '/' + relFile + '/')
					dic={'owner': int(userid),'username':user,'password':pas}
					progress_bar(str(server_url+'/user/' + user + '/data/' + str(p.name) + '/' + relFile) + '/',
								 dictic,dic, 1, s)
			else:
				dirlist = os.path.normpath(p.name + '/' + relFile)
				dirlist = dirlist.split(os.sep)
				for i in range(len(dirlist)):
					pat = str(p.name) + '/'
					for j in range(i):
						pat = pat + str(dirlist[j + 1]) + '/'

					r2 = s.get(server_url+'/user/' + user + '/contents/' + pat, data={'owner': int(userid)})

					if not r2.ok:
						owner = int(userid)
						username = user
						pat = ''
						for j in range(i):
							pat = pat + str(dirlist[j]) + '/'

						r2 = s.get(url=server_url+'/user/' + user + '/contents/' + pat, data={'owner': owner})

						if not r2.ok:
							parentid = 0
						else:
							data2 = r2.json()
							parentid = data2['pk']

						name = dirlist[i]
						pathLineage = pat + str(name) + '/'
						if i != len(dirlist) - 1:
							dorf = 'd'
							fileContent = '-'
							md5code = '-'
						else:
							md5code = md5(complete_path)
							dorf = 'f'
							with open(complete_path, 'rb') as inp:
								with open('outfile', 'wb') as out:
									base64.encode(inp, out)
							with open('outfile', 'rb') as con:
								content = con.readlines()
							# encrypt.encrypt(complete_path, enc_type,pas)
							# with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
							# 	content = con.read()
							# if os.path.exists(complete_path + '.' + enc_type + 'en'):
							# 	os.remove(complete_path + '.' + enc_type + 'en')
							fileContent = content
						dic = {'owner': owner, 'parentId': int(parentid), 'name': name, 'pathLineage': pathLineage,
							   'dorf': dorf,
							   'fileContent': fileContent, 'md5code': md5code, 'username': username}
						# print(dic)
						# print(server_url+'/user/' + user + '/data/' + pathLineage)
						dicti={}
						print('Adding ' + pathLineage)
						progress_bar(server_url+'/user/' + user + '/data/' + pathLineage,
									 dic,dicti, 0, s)

	r = s.get(url=server_url + '/user/' + user + '/allfiles/'+str(p.name), data={'owner': int(userid)})
	dat=r.json()
	# print(file_dir_list)
	for pat in dat:
		# print(pat['pathLineage'])

		if not pat['pathLineage'] in file_dir_list:
			dic = {'owner': int(userid), 'username': user, 'password': pas}
			dicti={}
			print('Deleting ' + pat['pathLineage'])
			progress_bar(server_url + '/user/' + user +'/data/'+pat['pathLineage'],dicti,dic,2,s)






