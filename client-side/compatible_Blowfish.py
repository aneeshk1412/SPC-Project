from Crypto.Cipher import Blowfish
from Crypto import Random
from struct import pack
import base64
import sys

def BloEnc(file_name , KEY ):
    IV = Random.get_random_bytes(8)

    try :
        filed = open(file_name, 'r')
        data = filed.read().encode()
        filed.close()
    except:
        filed = open(file_name , "rb")
        data = filed.read()
        filed.close()
        pass

    bs = Blowfish.block_size
    cipher = Blowfish.new(KEY, Blowfish.MODE_CBC , IV)
    plen = bs - len(data) % bs
    padding = [plen]*plen
    padding = pack('b'*plen, *padding)
    msg = IV + cipher.encrypt(data + padding)
    msg = base64.b64encode(msg)
    with open(file_name + '.bloen', 'wb') as outfile:
        outfile.write(msg)


def BloDec(msg , out_file , key):
    bs = Blowfish.block_size
    ciphertext= base64.b64decode(msg)
    iv = ciphertext[:bs]
    ciphertext = ciphertext[bs:]
    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    msg = cipher.decrypt(ciphertext)
    last_byte = msg[-1]
    msg = msg[:- (last_byte if type(last_byte) is int else ord(last_byte))]
    with open(out_file, 'wb') as f:
        f.write(msg)

if __name__ == '__main__':
    file = sys.argv[1]
    mess = BloEnc(file , "drumilt")
    BloDec(mess , file+"dec" ,"drumilt"  )