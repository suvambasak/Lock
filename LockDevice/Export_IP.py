import subprocess as sp
import urllib.request


op = sp.check_output("""ifconfig wifi0|grep "inet "|awk -F'[: ]+' '{ print $4 }'""",shell=True)

sendtext = op.decode().split()[0]
# print (sendtext)


try:
    resp = urllib.request.urlopen('https://techcodebox.000webhostapp.com/lock/device_ip.php?info='+sendtext)
    print (resp.read().decode())
except Exception as e:
    print (str(e))