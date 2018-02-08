# import urllib.request
#
#
# def onOffNotification(username, status = 'NONE', imageId = 'NONE'):
# 	if status == 'NONE':
# 		return
# 	if status == 'ON':
# 		response = urllib.request.urlopen('http://localhost/Lock/notify.php?username=' + username + '&msg=Yout%20Lock%20is%20now%20Online&type=ONOFF&imageId=null')
# 	elif status == 'OFF':
# 		response = urllib.request.urlopen('http://localhost/Lock/notify.php?username=' + username + '&msg=Yout%20Lock%20is%20now%20Offline&type=ONOFF&imageId=null')
# 	elif status == 'IMAGE':
# 		response = urllib.request.urlopen('http://localhost/Lock/notify.php?username=' + username + '&msg=Knock%20Knock!!&type=IMAGE&imageId=' + imageId)
# 	print(response.read())
#
#
# onOffNotification('basak',status='IMAGE',imageId='1')


# f = open("C:/xampp/htdocs/Lock/ServerBackup/basak/test.txt",'w')
f = open("C:/Users/Suvam Basak/test.txt",'w')
f.write("Hello world")
f.close()