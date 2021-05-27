from hashlib import md5
from base64 import b64decode
from base64 import b64encode
from Crypto import Random
from Crypto.Cipher import AES

# Padding for the input string --not
# related to encryption itself.
BLOCK_SIZE = 16  # Bytes


def pad(s): return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
    chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)


def unpad(s): return s[:-ord(s[len(s) - 1:])]


class AESCipher:
    """
    Usage:
            c = AESCipher('password').encrypt('message')
            m = AESCipher('password').decrypt(c)

    Tested under Python 3 and PyCrypto 2.6.1.

    """
    # pwd = '''~XeQk>'=N<q:_5KXz;4=3RL`X>qYZkG_">Kk[!QdEYTgT7xFe.^j&_6"s?-eyE#Yxs'htW8\sXQSBjEV=7~+K;r$]T/L;F""%_&N}R[vDm-7)Fw@RTj9[:,3wqVL)/:J'''

    def __init__(self):
        self.key = md5(self.get_key().encode('utf8')).hexdigest()

    def get_key(self):
        return open('key.pem', 'r').read()

    def encrypt(self, raw):
        raw = pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:])).decode('utf8')
