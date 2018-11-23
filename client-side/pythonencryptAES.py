from Crypto import Random
from Crypto.Cipher import AES
import base64
from pkcs7 import PKCS7Encoder

BLOCK_SIZE = 16
key = "1234567890123456" # want to be 16 chars
key = key.encode('utf-8')

def pad(data):
    length = 16 - (len(data) % 16)
    return data + chr(length)*length

def unpad(data):
    return data[:-ord(data[-1])]

def encrypt(infilename, passphrase):
    try:
        filed = open(infilename, 'r')
        message = filed.read()
        filed.close()
        message += ' ' * (16 - len(message) % 16)
        message = message.encode()
    except:
        filed = open(infilename, 'rb')
        message = filed.read()
        filed.close()
        message += b' ' * (16 - len(message) % 16)
        pass
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CFB, IV, segment_size=128)
    encryptedfilecontents = base64.b64encode(IV + aes.encrypt(message))
    with open(infilename+'.aesen', 'wb') as outfile:
        outfile.write(encryptedfilecontents)

def decrypt(filepath, encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CFB, IV, segment_size=128)
    decryptedfilecontents = aes.decrypt(encrypted[BLOCK_SIZE:])
    try:
    	decryptedfilecontents = unpad(decryptedfilecontents)
    	decryptedfilecontents = decryptedfilecontents.encode()
    except:
    	pass
    with open(filepath, 'wb') as outfile:
        outfile.write(decryptedfilecontents)


# # Encryption
# inp = 'This is a key123'
# inp = inp.encode('utf-8')
# iv4 = 'This is an IV456'
# encryption_suite = AES.new(inp, AES.MODE_CBC, iv4)
# cipher_text = encryption_suite.encrypt("A really secret message. Not for prying eyes.")
# print(cipher_text)
# # Decryption
# decryption_suite = AES.new(inp, AES.MODE_CBC, iv4)
# plain_text = decryption_suite.decrypt(cipher_text)
# print(plain_text)
# print(textToEncrypt)
# print(encrypt(textToEncrypt,key))
# if __name__ == '__main__':
# 	encrypt('decryptAES.txt', key)
# 	with open('decryptAES.txt.aesen','rb') as outfile:
# 		a = outfile.read()
# 	decrypt('res.txt', a, key)