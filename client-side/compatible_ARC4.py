from Crypto.Cipher import ARC4
import base64

# key = "123456"
# cipher = ARC4.new(key)
# text = "pedgree"
# msg = cipher.encrypt(text)
# print(msg)
# print(base64.b64encode(msg))
import sys

def ArcEnc(file_name , key ):
    try :
        filed = open(file_name, 'r')
        data = filed.read().encode()
        filed.close()
    except:
        filed = open(file_name , "rb")
        data = filed.read()
        filed.close()
        pass
    cipher = ARC4.new(key)
    msg = cipher.encrypt(data)
    #print(type(msg))
    with open(file_name + '.arcen', 'wb') as outfile:
        outfile.write(msg)
    return msg

def ArcDec(msg , out_file , key):
    cipher = ARC4.new(key)
    data = cipher.encrypt(msg)
    with open(out_file, 'wb') as f:
        f.write(data)

if __name__ == '__main__':
    file = sys.argv[1]
    mess = ArcEnc(file , "drumilt")
    ArcDec(mess , file+"dec" ,"drumilt"  )

