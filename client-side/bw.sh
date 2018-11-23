chmod +x spc.py
mkdir -p ~/bin
cp spc.py ~/bin/spc
cp sync.py ~/bin/sync.py
cp encrypt.py ~/bin/encrypt.py
cp pythonencryptAES.py ~/bin/pythonencryptAES.py
cp compatible_Blowfish.py ~/bin/compatible_Blowfish.py
<<<<<<< HEAD
cp bw_cron.py ~/bin/bw_cron.py



touch crontab.cron
echo '0 */2 * * * DISPLAY=:0 xterm -hold -e "python3 ~/bin/bw_cron.py" ' > crontab.cron
crontab crontab.cron


=======
cp compatible_ARC4.py ~/bin/compatible_ARC4.py
>>>>>>> 89f1818cf4bb93f8e9d8909fc06d51e42ed02155
export PATH=$PATH":$HOME/bin"

# sudo cp my_print /usr/local/man/man1/spc.1
# sudo gzip /usr/local/man/man1/spc.1
