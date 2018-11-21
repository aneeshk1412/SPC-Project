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



def progress_bar(ur,dat,b,s):
	widgets = [progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()]
	pbar = progressbar.ProgressBar(widgets=widgets)
	thread = threading.Thread(target=delete_post,
							  args=(ur,dat,b,s,))
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

def delete_post(ur, dat,b,s):
	if b==0:
		s.post(url=ur,data=dat)
	elif b==1:
		s.delete(ur)
		s.post(url=ur, data=dat)
	elif b==2:
		s.delete(ur)

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
		file_dir_list.append(dir_ + '/')
		for fileName in files:
			relDir = os.path.relpath(dir_, rootDir)
			relFile = os.path.join(relDir, fileName)
			file_dir_list.append(os.path.join(rootDir, relFile))
			if relFile[0:2] == "./":
				relFile = relFile[2:]
			dirname = str(p.name)
			st = str(server_url+'/user/' + user + '/contents/' + dirname + '/' + relFile) + '/'

			r2 = s.get(st, data={'owner': int(userid)})
			complete_path = os.path.join(rootDir, relFile)
			if (r2.ok):
				dicti = r2.json()
				if dicti['md5code'] != md5(complete_path):
					# with open(complete_path,'rb') as inp:
					# 	with open('outfile','wb') as out:
					# 		base64.encode(inp,out)
					# with open('outfile','rb') as con:
					# 	content=con.readlines()
					encrypt.encrypt(complete_path, enc_type,pas)
					with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
						content = con.readlines()
					if os.path.exists(complete_path + '.' + enc_type + 'en'):
						os.remove(complete_path + '.' + enc_type + 'en')
					# if(dicti['modifiedTime'] > datetime.fromtimestamp(os.stat(complete_path).st_mtime)):
					# 	ans=input('Do u want to modify this file? Y or N')
					# 	if(ans=='Y'):
					dicti['fileContent'] = content
					del dicti['modifiedTime']
					print('Replacing ' + str(p.name) + '/' + relFile + '/')
					progress_bar(str(server_url+'/user/' + user + '/data/' + str(p.name) + '/' + relFile) + '/',
								 dicti, 1, s)
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
							# with open(complete_path, 'rb') as inp:
							# 	with open('outfile', 'wb') as out:
							# 		base64.encode(inp, out)
							# with open('outfile', 'rb') as con:
							# 	content = con.readlines()
							encrypt.encrypt(complete_path, enc_type,pas)
							with open(complete_path + '.' + enc_type + 'en', 'rb') as con:
								content = con.read()
							if os.path.exists(complete_path + '.' + enc_type + 'en'):
								os.remove(complete_path + '.' + enc_type + 'en')
							fileContent = content
						dic = {'owner': owner, 'parentId': int(parentid), 'name': name, 'pathLineage': pathLineage,
							   'dorf': dorf,
							   'fileContent': fileContent, 'md5code': md5code, 'username': username}
						# print(dic)
						print('Adding ' + pathLineage)
						progress_bar(server_url+'/user/' + user + '/data/' + pathLineage,
									 dic, 0, s)

# r = s.get(url=server_url + '/user/' + user + '/list/', data={'owner': int(userid)})
# dat = r.json()
# for pat in dat:
# 	if not pat in file_dir_list:
# 		dic = {}
# 		print('Deleting ' + pat)
# 		progress_bar(server_url + '/user/' + user + '/data/' + pat, dic, 2, s)




