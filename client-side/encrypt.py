import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import hashlib
from Crypto.Cipher import DES3
from Crypto import Random

def DES3enc (in_filename):

    with open("iv.pem" , 'rb') as fiv:
        iv = fiv.read()
    with open("key.pem", 'rb') as fiv:
        key = fiv.read()
    out_filename = in_filename + ".de3en"
    des3 = DES3.new(key, DES3.MODE_CFB, iv)
    try:
        with open(in_filename, 'r') as in_file:
            with open(out_filename, 'wb') as out_file:
                while True:
                    chunk = in_file.read(8192)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)
                    chunk = chunk.encode()
                    out_file.write(des3.encrypt(chunk))
    except:
        with open(in_filename, 'rb') as in_file:
            with open(out_filename, 'wb') as out_file:
                while True:
                    chunk = in_file.read(8192)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)
                    out_file.write(des3.encrypt(chunk))
        pass

def DES3dec (in_filename ):
    with open("iv.pem" , 'rb') as fiv:
        iv = fiv.read()
    with open("key.pem", 'rb') as fiv:
        key = fiv.read()
    des3 = DES3.new(key, DES3.MODE_CFB, iv)
    with open(in_filename, 'rb') as in_file:
        with open("deccrypt.des3", 'wb') as out_file:
            while True:
                chunk = in_file.read(8192)
                if len(chunk) == 0:
                    break
                out_file.write(des3.decrypt(chunk))

def RSAenc (file):
    try:
        filed = open(file, 'r')
        data = filed.read().encode("utf-8")
        filed.close()
    except:
        filed = open(file, 'rb')
        data = filed.read()
        filed.close()
        pass

    des = file + ".rsaen"
    file_out = open(des, "wb")
    recipient_key = RSA.import_key(open("receiver.pem").read())
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    [file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]

def RSAdec (file):
    file_in = open(file, "rb")

    private_key = RSA.import_key(open("private.pem").read())

    enc_session_key, nonce, tag, ciphertext = \
        [file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    #print(data.decode("utf-8"))
    with open("decryt.rsa",'wb') as f:
        f.write(data)

def AESenc (file):
    try :
        filed = open(file, 'r')
        data = filed.read().encode()
        filed.close()
    except:
        filed = open(file , "rb")
        data = filed.read()
        filed.close()
        pass
    filek = open("AES.key", "rb")
    key = filek.read()
    filek.close()
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    des = file + ".aesen"
    file_out = open( des , "wb")
    [file_out.write(x) for x in (cipher.nonce, tag, ciphertext)]

def AESdec (file):
    file_in = open(file, "rb")
    nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
    filek = open('AES.key', 'rb')
    key = filek.read()
    filek.close()
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    with open("decryt.aes",'wb') as f:
        f.write(data)
    #print(data)

def encrypt(file_name , choice , passwordt):
    passwordt = passwordt.encode()

    if not os.path.exists("AES.key"):
        key = hashlib.sha256(passwordt).digest()
       #key = get_random_bytes(16)
        print(key)
        file = open('AES.key', 'wb')
        file.write(key)
        file.close()

    # if not os.path.exists("RSA.key"):
    #     secret_code = "Unguessable"
    #     key = RSA.generate(2048)
    #     encrypted_key = key.export_key(passphrase=secret_code, pkcs=8,
    #                                    protection="scryptAndAES128-CBC")
    #     file_out = open("RSA.key", "wb")
    #     file_out.write(encrypted_key)
    #     print(key.publickey().export_key())

    if (not os.path.exists("iv.pem")) or (not os.path.exists("key.pem")):
        key = hashlib.md5(passwordt).digest()
        print(key)
        file_out = open("key.pem", "wb")
        file_out.write(key)
        m = hashlib.sha224()
        m.update(passwordt)
        iv = m.digest()[:8]
        print(iv)
        #iv = Random.get_random_bytes(8)
        file_out = open("iv.pem", "wb")
        file_out.write(iv)


    if not os.path.exists("receiver.pem"):
        key = RSA.generate(2048)
        print(key)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)
        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

    file = file_name
    if(choice=='aes'):
        AESenc(file)
        file = file + ".aesen"
        AESdec(file)
    elif (choice=='rsa'):
        RSAenc(file)
        file = file + ".rsaen"
        RSAdec(file)
    elif (choice=='des3'):
        DES3enc(file)
        file = file + ".de3en"
        DES3dec(file)
    else:
        print("Invalid try again")

def decrypt(file_name):
    choice = file_name[-5:-2:1]
    print(choice)
    if (choice == 'aes'):
        AESdec(file_name)
    elif (choice == 'rsa'):
        RSAdec(file_name)
    elif (choice == 'de3'):
        DES3dec(file_name)
    else:
        print("Invalid try again")

if __name__ == '__main__':
    file = sys.argv[1]
    choice = sys.argv[2]
    passwordt = sys.argv[3]
    encrypt(file, choice , passwordt)
    #decrypt()