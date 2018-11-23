import subprocess
import os

if os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/auth.txt"))) and os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/enc.txt"))) and os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/dir.txt"))) and os.path.exists(os.path.expanduser(os.path.join("~", "spc_details/ur.txt"))):
	user_response = input('Do u wish to do periodic sync (y or n): ')
	if user_response == 'y':
		subprocess.run('~/bin/spc sync',shell=True)
		print('sync complete')