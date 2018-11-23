from Crypto import Random
from Crypto.Cipher import AES
import base64
from pkcs7 import PKCS7Encoder

BLOCK_SIZE = 16
key = "1234567890123456" # want to be 16 chars
key = key.encode('utf-8')
textToEncrypt = "This is text to encrypt"

def pad(data):
    length = 16 - (len(data) % 16)
    return data + chr(length)*length

def unpad(data):
    data = data.decode('utf-8')
    return data[:-ord(data[-1])]

def encrypt(message, passphrase):
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CFB, IV, segment_size=128)
    return base64.b64encode(IV + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CFB, IV, segment_size=128)
    return unpad(aes.decrypt(encrypted[BLOCK_SIZE:]))


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
print(textToEncrypt)
print(encrypt(textToEncrypt,key))
s = encrypt(textToEncrypt,key)
print(decrypt(s,key))
