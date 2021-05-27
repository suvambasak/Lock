from uuid import getnode
import MakeHash
mac = getnode()


def getMACInInt():
    return mac


def getMACInHex():
    return hex(mac)


def getMACHash():
    hash = MakeHash.getHash(str(mac))
    return hash
