chmod +x spc.py
mkdir -p ~/bin
cp spc.py ~/bin/spc
cp sync.py ~/bin/sync.py
cp encrypt.py ~/bin/encrypt.py
cp pythonencryptAES.py ~/bin/pythonencryptAES.py
export PATH=$PATH":$HOME/bin"

# sudo cp my_print /usr/local/man/man1/spc.1
# sudo gzip /usr/local/man/man1/spc.1
