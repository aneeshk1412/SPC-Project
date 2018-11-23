chmod +x spc.py
# python3 -m pip install -r "requirements.txt"
mkdir -p ~/bin
cp spc.py ~/bin/spc
cp sync.py ~/bin/sync.py
cp encrypt.py ~/bin/encrypt.py
cp pythonencryptAES.py ~/bin/pythonencryptAES.py
cp compatible_Blowfish.py ~/bin/compatible_Blowfish.py
cp compatible_ARC4.py ~/bin/compatible_ARC4.py
cp bw_cron.py ~/bin/bw_cron.py



touch crontab.cron
echo '0 */2 * * * DISPLAY=:0 xterm -hold -e "python3 ~/bin/bw_cron.py" ' > crontab.cron
crontab crontab.cron



export PATH=$PATH":$HOME/bin"

c=$(sudo ls /usr/local/man | grep man)
sudo cp my_spc /usr/local/man/$c/spc.1
sudo gzip /usr/local/man/$c/spc.1
