import urllib.request
import json
import Database
#
# email = 'suvambasak2008@gmail.com'
# username = 'basak'
# text = 'hello world'
# id = 3
# android = '46d550fd4216a595dead885eec8ec34'
# db = Database.Database()
#
# print (
# 	db.submit_notify(username,email, 'Image Taken', 1)
# )






def onOffNotification(username, status = 'NONE', imageId = 'NONE'):
	if status == 'NONE':
		return
	if status == 'ON':
		response = urllib.request.urlopen('http://localhost/LockBackend/notify.php?username=' + username + '&msg=Yout%20Lock%20is%20now%20Online&type=ONOFF&imageId=null')
	elif status == 'OFF':
		response = urllib.request.urlopen('http://localhost/LockBackend/notify.php?username=' + username + '&msg=Yout%20Lock%20is%20now%20Offline&type=ONOFF&imageId=null')
	elif status == 'IMAGE':
		response = urllib.request.urlopen('http://localhost/LockBackend/notify.php?username=' + username + '&msg=Knock%20Knock!!&type=IMAGE&imageId=' + imageId)
	print(response.read())


onOffNotification('basak',status='OFF')


# username = 'basak'
# response = urllib.request.urlopen('http://localhost/Lock/notify.php?username=' + username + '&msg=Yout%20Lock%20is%20now%20Online&type=ONOFF&imageId=null')
# response_log = response.read().decode()
# response_log = response_log.split()
# response_log = response_log[1]
# response_log_trim = response_log[1:]
# response_log_trim = response_log_trim[:-1]
# response_json = json.loads(response_log_trim)
#
# print ('#####   Notification Info   #####')
# print ('multicast_id :: ',response_json['multicast_id'])
# print ('success :: ',response_json['success'])
# print ('failure :: ',response_json['failure'])
# print ('canonical_ids :: ',response_json['canonical_ids'])
# print (response_json['results'])






