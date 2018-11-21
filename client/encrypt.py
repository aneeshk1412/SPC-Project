import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import hashlib
from Crypto.Cipher import DES3

def DES3enc (in_filename, chunk_size, key, iv):
    out_filename = in_filename + ".ds3en"
    des3 = DES3.new(key, DES3.MODE_CFB, iv)
    with open(in_filename, 'r') as in_file:
        with open(out_filename, 'w') as out_file:
            while True:
                chunk = in_file.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                out_file.write(des3.encrypt(chunk))

def DES3dec (in_filename, out_filename , chunk_size, key, iv):
    des3 = DES3.new(key, DES3.MODE_CFB, iv)
    with open(in_filename, 'r') as in_file:
        with open(out_filename, 'w') as out_file:
            while True:

                chunk = in_file.read(chunk_size)
                if len(chunk) == 0:
                    break
                out_file.write(des3.decrypt(chunk))

def RSAenc (file):
    filed = open(file, 'r')
    data = filed.read().encode("utf-8")
    filed.close()

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
    print(data.decode("utf-8"))


def AESenc (file):
    filed = open(file, 'r')
    data = filed.read().encode("utf-8")
    filed.close()
    filek = open("AES.key", "rb")
    key = filek.read()
    filek.close()
    #print(key)
    #key = get_random_bytes(16)
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
    data=  data.decode()
    print(data)

if __name__ == '__main__':


    # with open('pass.txt' , 'r') as f :
    #     passwordt = f.read()

    passwordt = 'password'
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

    if not os.path.exists("receiver.pem"):
        key = RSA.generate(2048)
        print(key)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

    file = sys.argv[1]
    choice= input("What encrytion schema do you need ? a) AES b) RSA c) DES3")
    if(choice=='a'):
        AESenc(file)
        file = file + ".aesen"
        AESdec(file)
    elif (choice=='b'):
        RSAenc(file)
        file = file + ".rsaen"
        RSAdec(file)
    elif (choice=='c'):
        DES3enc(file)
        file = file + ".des3en"
        DES3dec(file)
    else:
        print("Invalid try again")



