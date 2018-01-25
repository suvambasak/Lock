from _thread import *
import SendEmail as email
import Database as db
import ImageEncoderDecoder as ImageEncoder
import Forward
import threading
import socket
import time
import json
import sys
import os
import urllib.request


###############################################    NOTIFICATION   ##########################################################
def onOffNotification(username, status='NONE', imageId='NONE'):
	if status == 'NONE':
		return
	if status == 'ON':
		response = urllib.request.urlopen(
			'http://localhost/Lock/notify.php?username=' + username + '&msg=Your%20Lock%20is%20now%20Online&type=ONOFF&imageId=null')
	elif status == 'OFF':
		response = urllib.request.urlopen(
			'http://localhost/Lock/notify.php?username=' + username + '&msg=Your%20Lock%20is%20now%20Offline&type=ONOFF&imageId=null')
	elif status == 'IMAGE':
		response = urllib.request.urlopen(
			'http://localhost/Lock/notify.php?username=' + username + '&msg=Knock%20Knock!!&type=IMAGE&imageId=' + imageId)
	print(response.read())


###############################################   BACK-UP SOCKET SERVER CLASS   ############################################

class BackupServer:
	'Back up server - Containing socket server & connection handler & backup function & notify with photo via email'

	def __init__(self, host, port):
		# initilizing class variables.
		self.host = host
		self.port = port
		self.database = db.Database()

		# creating socket object
		self.server = socket.socket()

		# address binding.
		try:
			self.server.bind((self.host, self.port))
			self.server.listen()
			print('\n[*] BACK-UP server is running at -' + str((self.host, self.port)))

			# calling the backup connection handler function.
			self.backUpServerConnectionHandler()
		except Exception as e:
			print('\n[**] Exception :: Back up Server address bind :: ' + str(e))


			# connection handler function. accept connection and call backup to take image backup.

	def backUpServerConnectionHandler(self):
		print('\n[*] Back-up server connection handler is running.')

		# global variable for to controling backup server.
		global backupServerControl

		while backupServerControl:
			try:
				# accepting the connection.
				connection, address = self.server.accept()

				if backupServerControl:
					print('\n[*] Back-up Server Connected by - ' + str(address))
					# creating a thread for each connection.
					start_new_thread(self.backup, (connection,))
				else:
					break

			except Exception as e:
				print('[**] Exception :: Back-up server connection accept :: ' + str(e))


				# function for taking backup.

	def backup(self, connection):
		try:
			# get jSON of filename and username.
			jsonFilename = connection.recv(1024).decode()

			# format of filename.
			# filename['name']
			# filename['username']

			# convert to python dictionary.
			filename = json.loads(jsonFilename)
			print('\n[*] File name recieved : ' + filename['name'])

			# open a file in :: ServerBackup/username/filename directory.
			with open('ServerBackup/' + filename['username'] + '/' + filename['name'], 'wb') as file:
				print('\n\n[*] file open')
				print('[*] fetching file...')

				# fetching file.
				while True:
					fileContent = connection.recv(2048)
					# checking file content.
					if not fileContent:
						break

					# Writing the file conetnt into the file.
					file.write(fileContent)

				# close the file fetching complete.
				file.close()

				# file encoding.
				path = ImageEncoder.encode('ServerBackup/' + filename['username'] + '/' + filename['name'])
				# updating the Database and getting tuple id
				updateId = self.database.insertImageBackup(filename['username'], path)

				print('\n[*] ' + filename['name'] + ' Back-up Done.')

				# sending image to owner as email.
				if filename['email'] == 'YES':
					email.sendImage(filename['username'],
									'ServerBackup/' + filename['username'] + '/' + filename['name'])
				elif filename['bell'] == 'YES':
					onOffNotification(filename['username'], status='IMAGE', imageId=str(updateId))
				else:
					self.database.submitNotify(filename['username'], filename['emailId'],'Image Taken', updateId)

				# remove the image file.
				os.remove('ServerBackup/' + filename['username'] + '/' + filename['name'])
		except Exception as e:
			print('[**] Exception :: backup :: ' + str(e))


#################################################### LOCK DEVICE CLASS ###################################################

class LockDevice:
	'Lock Device class - Containing Device online tracker & directory create method & connected device list (connectionList).'
	# initilization of global connection dictionary.
	global connectionList

	# initilization function of the class.
	def __init__(self, connection, deviceIp, username, mac):
		# initilizing the class variables.
		self.connection = connection
		self.ip = deviceIp
		self.username = username
		self.MAC = mac
		self.database = db.Database()

		# updating global connection dictionary
		connectionList[username] = connection
		# inserting into database.
		self.database.insertOnlineDevice(self.username)

		# calling the class function.
		self.createDirectory()
		self.printDetails()
		# creating one thread for online Tracking function.
		start_new_thread(self.onlineTrack, (True,))
		# Send notification to all phones.
		onOffNotification(self.username, status='ON')

	# online tracking function
	def onlineTrack(self, loop):
		# track message dictionary.
		track = {}
		track['request'] = ''
		track['message'] = 'online'
		# converting into JSON.
		jsonTrack = json.dumps(track)

		while loop:
			try:
				# sending JSON track.
				# track['request'] = ''
				# track['message'] = 'online'

				self.connection.send(str.encode(jsonTrack))
				time.sleep(3)

				# Getting reply from Lock device.
				# track['message'] = 'online'
				# track['reply'] = 'online'
				deviceReply = self.connection.recv(2014).decode()

				deviceReply = json.loads(deviceReply)

				# checking reply
				# if not reply the exit the loop and destroy the object.
				if deviceReply['reply'] != 'online':
					loop = False
					break

				print('\n[*]Lock :: ' + str(self.username) + ' IP :: ' + str(self.ip) + '  STATUS ' + str(deviceReply))
			except Exception as e:
				print('\n[**] Exception Online Tracking :: ' + str(e))
				loop = False


				# function for creating the directory for the username.

	def createDirectory(self):
		if not os.path.exists('ServerBackup/' + self.username):
			os.makedirs('ServerBackup/' + self.username)

			# function for printing details.

	def printDetails(self):
		print('\n')
		print('\n\n[*] LOCK >> username ' + str(self.username) + ' IP ' + str(self.ip) + ' Initilazing done.')
		print('\n')

	# function for self destroy.
	def __del__(self):
		# delete from online db.
		self.database.deleteOnlineDevice(self.username)
		# sending a email to owner for the lock device is disconnected.
		start_new_thread(email.disconnectAlert, (self.username,))
		# Send notification to all phones
		onOffNotification(self.username, status='OFF')

		# deleting the connection from global connection dictionary.
		del connectionList[self.username]
		class_name = self.__class__.__name__
		print('\n\n', self.username, 'destroyed')


################################################    MAIN SERVER CONNECTION HANDLER FUNCTION    ###########################

def connectionHandler(connection, ip):
	try:
		request = connection.recv(1024).decode()
		request = json.loads(request)
		database = db.Database()

	### JSON for phone.
	# print("Device  : " + request['device'])
	# print("username : " + request['username'])
	# print("androi ID : " + request['androidId'])
	# print("request : " + request['request'])

	### JSON for Lock Device.
	# print("Device  : " + request['device'])
	# print("username : " + request['username'])
	# print("MAC address : " + request['mac'])
	except Exception as e:
		print('ok')

	# checking device type phone.
	if request['device'] == 'Phone':
		# checking android ID.
		if (database.checkAndroidId(request['username'], request['androidId']) or database.checkMemberAndroidId(
				request['username'], request['androidId'])):

			# printing details.
			print('\n[**] Device Details::\n')
			print("Device  : " + request['device'])
			print("username : " + request['username'])
			print("Android ID : " + request['androidId'])
			print("Email : " + request['email'])
			print("Request : " + request['request'])

			print('[**] Device Android ID Matched.')

			# initilizing global connection list.
			global connectionList

			# checking connection exist or not.
			if request['username'] in connectionList:
				# starting thread for forwarding the request.
				# passing request, Lock connection object, phone connection object as agrument.
				start_new_thread(Forward.requestForward,
								 (request['request'], request['email'], connectionList[request['username']], connection))
			else:
				# if the connection is not present in the connection list.
				# sending reply.
				connection.sendall(str.encode('Offline.\n'))


		# if android ID is not matching.
		else:
			print('[**] Device Android ID is not Matched.')
			# sending reply.
			connection.sendall(str.encode('Un-known Device.\n'))


	# checking the device type Lock Device.
	elif request['device'] == 'LockDevice':

		# Checking MAC address of the lock
		if (database.checkLockMAC(request['username'], request['mac'])):

			# printing details.
			print('\n[**] Device Details::\n')
			print("Device  : " + request['device'])
			print("username : " + request['username'])
			print("MAC address : " + request['mac'])

			print('[**] Lock Device MAC is Matched.')

			# Creating object of Lock Device.
			LockDevice(connection, ip, request['username'], request['mac'])

		# if MAC Address is not matched.
		else:
			print('[**] Lock Device MAC Address is not Matched.')
			# Sending reply.
			# connection.sendall(str.encode('MAC Address is not matched...'))

	# when incoming data fromat is unknown.
	else:
		connection.close()
		print('[***] Fully Unknown Device.')


######################################################    MAIN FUNCTION     ##############################################

# check for serverBackup path and create.
if not os.path.exists('ServerBackup'):
	os.makedirs('ServerBackup')

# global variables :: host and usernameList.
global host, connectionList, phoneConnectionList, backupServerControl
# backup server Control
backupServerControl = True
# Declare connectionList a Dictionary.
connectionList = {}
phoneConnectionList = {}
# Server IPv4 and port and backup port.
host = socket.gethostbyname(socket.gethostname())
port = 9000
backupPort = 9999
# creating server object.
server = socket.socket()

# Creating a thread of backup server.
backup = threading.Thread(target=BackupServer, args=(host, backupPort), name="backupThread")
# binding IP and port number.
try:
	server.bind((host, port))

	# start the backup server.
	backup.start()

except Exception as e:
	print('\n[**] Exception :: address binding :: ' + str(e))
	sys.exit(1)

# putting server into listen mode.
server.listen(100)

# printing status
print('\n[*] Main Server is running at :: ' + str((host, port)))

# accepting connection and forwarding connection to connection handler.
try:
	while True:
		try:
			connection, address = server.accept()
			print('\n[**] Main Server connected by - ' + str(address))
			start_new_thread(connectionHandler, (connection, address[0]))
		except Exception as e:
			print('\n[**] Exception :: server connection :: ' + e)
except KeyboardInterrupt as e:
	print('-\n' * 5)
	print('\n[*] Stopping Main Server....')
	time.sleep(0.5)
	server.close()
	print('\n[*] Done.')

	# stoppin the backup server by deleting object.
	print('\n[*] Stopping the Back-up Server...')

	# Stopping the loop.
	backupServerControl = False
	# dummy client to exit the loop.
	dummy = socket.socket()
	dummy.connect((host, backupPort))
	dummy.close()
	# join the backup server thread.
	backup.join()

	time.sleep(0.5)
	print('\n[*] Done\n\n')
finally:
	database = db.Database()
	database.deleteAllOnlineDevice()