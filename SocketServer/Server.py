from _thread import *
import SendEmail as email
import Database as db
import ImageEncoderDecoder as ImageEncoder
import Forward
import platform
import subprocess
import threading
import socket
import time
import json
import sys
import os
import urllib.request
import urllib.request
from AES import AESCipher

# -----------------------------    NOTIFICATION   ------------------------------------------
def on_off_notification(username, status='NONE', image_id='NONE', msg=None):
	if status == 'NONE':
		return
	if status == 'ON':
		response = urllib.request.urlopen(
			'http://localhost/LockBackend/notify.php?username=' + username + '&msg=Your%20Lock%20is%20now%20Online&type=ONOFF&imageId=null')
	elif status == 'OFF':
		response = urllib.request.urlopen(
			'http://localhost/LockBackend/notify.php?username=' + username + '&msg=Your%20Lock%20is%20now%20Offline&type=ONOFF&imageId=null')
	elif status == 'SPY':
		text = msg.replace(' ','%20')
		response = urllib.request.urlopen(
			'http://localhost/LockBackend/notify.php?username=' + username + '&msg='+text+'&type=IMAGE&imageId=' + image_id)
	elif status == 'IMAGE':
		response = urllib.request.urlopen(
			'http://localhost/LockBackend/notify.php?username=' + username + '&msg=Knock%20Knock!!&type=IMAGE&imageId=' + image_id)

	response_log = response.read().decode()
	response_log = response_log.split()
	response_log = response_log[1]

	response_log_trim = response_log[1:]
	response_log_trim = response_log_trim[:-1]

	response_json = json.loads(response_log_trim)

	print('#####   Notification Info   #####')

	print('multicast_id :: ', response_json['multicast_id'])
	print('success :: ', response_json['success'])
	print('failure :: ', response_json['failure'])
	print('canonical_ids :: ', response_json['canonical_ids'])
	print(response_json['results'])


# ---------------------   BACK-UP SOCKET SERVER CLASS   ------------------------
class BackupServer:
	"""Back up server - Containing socket server & connection handler & backup function & notify with photo via email"""

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
			self.backup_server_connection_handler()
		except Exception as e:
			print('\n[**] Exception :: Back up Server address bind :: ' + str(e))

	# connection handler function. accept connection and call backup to take image backup.

	def backup_server_connection_handler(self):
		print('\n[*] Back-up server connection handler is running.')

		# global variable for to controling backup server.
		global backup_server_control

		while backup_server_control:
			try:
				# accepting the connection.
				connection, address = self.server.accept()

				if backup_server_control:
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
					file_content = connection.recv(2048)
					# checking file content.
					if not file_content:
						break

					# Writing the file conetnt into the file.
					file.write(file_content)

				# close the file fetching complete.
				file.close()

				# file encoding.
				path = ImageEncoder.encode('ServerBackup/' + filename['username'] + '/' + filename['name'])
				# updating the Database and getting tuple id
				update_id = self.database.insert_image_backup(filename['username'], path)

				print('\n[*] ' + filename['name'] + ' Back-up Done.')

				# sending image to owner as email.
				if filename['email'] == 'YES':
					email.send_image(filename['username'],
									 'ServerBackup/' + filename['username'] + '/' + filename['name'])
				elif filename['bell'] == 'YES':
					on_off_notification(filename['username'], status='IMAGE', image_id=str(update_id))
				elif filename['spy'] == 'YES':
					on_off_notification(filename['username'], status='SPY', image_id=str(update_id), msg=filename['info'])
				else:
					self.database.submit_notify(filename['username'], filename['emailId'], 'Image Taken', update_id)

				# remove the image file.
				os.remove('ServerBackup/' + filename['username'] + '/' + filename['name'])
		except Exception as e:
			print('[**] Exception :: backup :: ' + str(e))


# --------------------------- LOCK DEVICE CLASS -------------------------------------------
class LockDevice:
	"""Lock Device class - Containing Device online tracker & directory create method & connected device list (
	connectionList). """

	global connection_list

	# initial function of the class.
	def __init__(self, connection, deviceIp, username, mac):
		# initilize the class variables.
		self.connection = connection
		self.ip = deviceIp
		self.username = username
		self.MAC = mac
		self.database = db.Database()

		# updating global connection dictionary
		connection_list[username] = connection
		# inserting into database.
		self.database.insert_online_device(self.username)

		# calling the class function.
		self.create_directory()
		self.print_details()
		# creating one thread for online Tracking function.
		start_new_thread(self.online_track, (True,))
		# Send notification to all phones.
		on_off_notification(self.username, status='ON')

	# online tracking function
	def online_track(self, loop):
		# track message dictionary.
		track = {}
		track['request'] = ''
		track['message'] = 'online'
		# converting into JSON.
		json_track = json.dumps(track)

		#encryption
		cipher = AESCipher().encrypt(json_track)

		while loop:
			try:
				# sending JSON track.
				# track['request'] = ''
				# track['message'] = 'online'

				self.connection.send(cipher)
				time.sleep(3)

				# Getting reply from Lock device.
				# track['message'] = 'online'
				# track['reply'] = 'online'
				device_reply_cipher = self.connection.recv(2014).decode()
				# print(device_reply_cipher)

				#decryption
				device_reply = AESCipher().decrypt(device_reply_cipher)

				device_reply = json.loads(device_reply)

				# checking reply
				# if not reply the exit the loop and destroy the object.
				if device_reply['reply'] != 'online':
					loop = False
					break

				print('\n[*]Lock :: ' + str(self.username) + ' IP :: ' + str(self.ip) + '  STATUS ' + str(device_reply))
			except Exception as e:
				print('\n[**] Exception Online Tracking :: ' + str(e))
				loop = False

	# function for creating the directory for the username.

	def create_directory(self):
		if not os.path.exists('ServerBackup/' + self.username):
			os.makedirs('ServerBackup/' + self.username)

	# function for printing details.

	def print_details(self):
		print('\n')
		print('\n\n[*] LOCK >> username ' + str(self.username) + ' IP ' + str(self.ip) + ' Initilazing done.')
		print('\n')

	# function for self destroy.
	def __del__(self):
		# delete from online db.
		self.database.delete_online_device(self.username)
		# sending a email to owner for the lock device is disconnected.
		start_new_thread(email.disconnect_alert, (self.username,))
		# Send notification to all phones
		on_off_notification(self.username, status='OFF')

		# deleting the connection from global connection dictionary.
		del connection_list[self.username]
		class_name = self.__class__.__name__
		print('\n\n', self.username, 'destroyed')


################################################    MAIN SERVER CONNECTION HANDLER FUNCTION    ###########################

def connection_handler(connection, ip):
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
		if database.user_authentication(request['username'], request['androidId'],request['email']):

			# printing details.
			print('\n[**] Device Details::\n')
			print("Device  : " + request['device'])
			print("username : " + request['username'])
			print("Android ID : " + request['androidId'])
			print("Email : " + request['email'])
			print("Request : " + request['request'])

			print('[**] Device Android ID Matched.')

			# initilizing global connection list.
			global connection_list

			# checking connection exist or not.
			if request['username'] in connection_list:
				# starting thread for forwarding the request.
				# passing request, Lock connection object, phone connection object as agrument.
				start_new_thread(Forward.request_forward,
								 (
									 request['request'], request['email'], connection_list[request['username']],
									 connection))
			else:
				# if the connection is not present in the connection list.
				# sending reply.
				connection.sendall(str.encode('Lock-Disconnected.\n'))

		# if android ID is not matching.
		else:
			print('[**] Device Request Rejected.')
			# sending reply.
			connection.sendall(str.encode('Un-known Device.\n'))

	# checking the device type Lock Device.
	elif request['device'] == 'LockDevice':

		# Checking MAC address of the lock
		if (database.check_lock_mac(request['username'], request['mac'])):

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
			print('[**] Lock Device MAC Address is NOT Matched.')
	# Sending reply.
	# connection.sendall(str.encode('MAC Address is not matched...'))

	# when incoming data fromat is unknown.
	else:
		connection.close()
		print('[***] Fully Unknown Device.')


# function for updating server ip address.
def update_server_config(host):
	try:
		print("[*] Updating Server Credentials.\n")
		print("Please Wait...")
		resp = urllib.request.urlopen('https://techcodebox.000webhostapp.com/lock/server_ip.php?info=' + host)
		print(resp.read().decode())
	except Exception as e:
		print('\n[**] Exception :: update server config :: ' + str(e))


# ------------------------- MAIN FUNCTION ----------------------

# check for serverBackup path and create.
if not os.path.exists('ServerBackup'):
	os.makedirs('ServerBackup')

# global variables :: host and usernameList.
global host, connection_list, phone_connection_list, backup_server_control

# backup server Control
backup_server_control = True

# Declare connection List a Dictionary.
connection_list = {}
phone_connection_list = {}

# Server IPv4 for Windows.
if platform.system() == 'Windows':
	print("Platform :: Windows\n")
	host = socket.gethostbyname(socket.gethostname())
	print("Ipv4 Found :: ", host, '\n')

# Server IPv4 for Linux.
elif platform.system() == 'Linux':
	print("Platform :: Linux\n")
	host = subprocess.check_output("""ifconfig wlp6s0|grep "inet "|awk -F'[: ]+' '{ print $4 }'""",
								   shell=True).decode().split()[0]
	print("Ipv4 Found :: ", host, '\n')

# Server IPv4 for Unknown system.
else:
	print("Unknown System Please Enter IPv4 manually..\n")
	host = input("Server IPv4 :: ")

# Server port and backup port.
port = 9000
backupPort = 9999

# calliing server update function for updating IP.
update_server_config(host)

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
			start_new_thread(connection_handler, (connection, address[0]))

		except Exception as e:
			print('\n[**] Exception :: server connection :: ' + e)

except KeyboardInterrupt as e:
	print('-\n' * 5)
	print('\n[*] Stopping Main Server....')
	time.sleep(0.5)
	server.close()
	print('\n[*] Done.')

	# stopping the backup server by deleting object.
	print('\n[*] Stopping the Back-up Server...')

	# Stopping the loop.
	backup_server_control = False

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
	database.delete_all_online_device()
