# importing lib
import hashlib

# method tor converting hash.


def getHash(text):
    # making hash and return the hash.
    hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return hash
