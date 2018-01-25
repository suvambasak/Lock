import MAC as physicalAddress
import socket
import threading
import json
import time
import sys
# import CaptureImage as camera
import CaptureImagePC as camera


# Send image function.
# parameter Email, Bell
def sendImage(emailId,email = False, bell = False):
	global host, username

	try:
		# retrive the file name.
		number = str(open('ProgramData/numberFile', 'r').read())
		name = 'imgCL' + number + '.png'

		# creating filename & username JSON object.
		filename = {}
		filename['name'] = name
		filename['username'] = username
		filename['emailId'] = emailId

		if email:
			filename['email'] = 'YES'
			filename['bell'] = 'NO'
		elif bell:
			filename['email'] = 'NO'
			filename['bell'] = 'YES'
		else:
			filename['email'] = 'NO'
			filename['bell'] = 'NO'

		jsonFilename = json.dumps(filename)

		# creating socket object.
		backupServer = socket.socket()

		# connecting to the backup server.
		backupServer.connect((host, 9999))
		# send the JSON objet containing filename and username.
		backupServer.send(str.encode(jsonFilename))
		time.sleep(2)

		# path to the file.
		# and read the file content
		path = 'ProgramData/' + name
		file = open(path, 'rb')
		fileContent = file.read(2048)

		# send the file content until complete.
		while (fileContent):
			backupServer.send(fileContent)
			fileContent = file.read(2048)
		file.close()

		backupServer.close()

	except Exception as e:
		print ('[*] Exception :: Image send :: ' + str(e))



# Take image function.
def takeImage( emailId,email=False):
	# initilizing global variables
	global cameraLock, host, username
	print ('\n[||] Email :: ' + str(email))
	# locking the camera to prevent another thread to use camera.
	cameraLock.acquire()
	try:
		# execute the FileName.py for take the image.
		camera.capture()
		time.sleep(2)

		# checking for email request ot Take image request.
		if email:
			sendImage(emailId,email=True)
		else:
			sendImage(emailId)

	except Exception as e:
		print ('[**] Exception :: Take Image function :: ' + str(e))
	finally:
		print ('[*] Done')

		# releasing the lock when execution of the method complete.
		cameraLock.release()
		print ('\n-' * 5)



# calling Bell Event
def callingBell():
	# global variable of camera lock and
	global cameraLock, bellActivator, host, username
	while bellActivator:
		# waiting for calling bell presss
		# for pc enter is the button for calling bell.
		press = input()
		if bellActivator:
			print ('[*] Calling Bell pressed.')
			cameraLock.acquire()

			try:
				# execute the FileName.py for take the image.
				# camera.capture()
				time.sleep(2)

				# sending the image.
				sendImage(None,bell=True)

				print ('complete')
			except Exception as e:
				print ('[**] Exception :: callingBell :: ' + str(e))
			finally:
				cameraLock.release()



# global veriable.
global username, MAC, host, jsonInfo, cameraLock, doorLock, bellActivator

# Setting username MAC address Host IPv4 and post number.
username = 'basak'
MAC = physicalAddress.getMACHash()
host = str(sys.argv[1])
post = 9000

bellActivator = True
# thread locks || one camera lock || one door lock.
doorLock = threading.Lock()
cameraLock = threading.Lock()

callingBellThread = threading.Thread(target=callingBell, name="bell")




# creating identity json
info = {}
info['device'] = 'LockDevice'
info['username'] = username
info['mac'] = MAC
jsonInfo = json.dumps(info)

# socket object.
device  = socket.socket()

# connecting to main server
try:
	device.connect((host,post))
	device.send(str.encode(jsonInfo))
except Exception as e:
	print ('[**] Exception :: Connecting to Main server :: ' + str(e))


# off/on try catch block.
try:
	# starting calling bell thread.
	callingBellThread.start()
	# main loop for receiving and replying message/request.
	while True:
		try:
			request = device.recv(1024).decode()
			# loads the JSON.
			request = json.loads(request)
			print (request)

		except Exception as e:
			print('[**] Exception :: receiving the data :: ' + str(e))

		# server track JSON.
		# track['request'] = ''
		# track['message'] = 'online'

		# server waiting for.
		# track['message'] = 'online'
		# track['reply'] = 'online'

		if request['message'] == 'online':
			# creating response of online track.
			response = {}
			response['message'] = 'online'
			response['reply'] = 'online'

			# creating JSON response.
			jsonResponse = json.dumps(response)

			# replying to the server.
			device.send(str.encode(jsonResponse))

		# Lock request.
		elif request['request'] == 'Lock':
			print ('Requesting for : LOCK')

		# Unlock request.
		elif request['request'] == 'Unlock':
			print('Requesting for : UNLOCK')


		# TakeImage request.
		elif request['request'] == 'TakeImage':
			print ('Requesting for : TAKE IMAGE')

			# creating a thread for take image function.
			takeImageFunction = threading.Thread(target=takeImage,args=(request['email'],False), name='functionTakeImage')
			takeImageFunction.start()


		# Email request.
		elif request['request'] == 'Email':
			print ('Requesting for : EMAIL')
			# creating a thread for Email image.
			emailImageFunction = threading.Thread(target=takeImage,args=(request['email'],True) , name='functionEmailImage')
			emailImageFunction.start()

except KeyboardInterrupt as e:
	print('\n-' * 5)
	print('[*] Connection closing...')
	device.close()
	time.sleep(0.5)
	# stopping Calling bell loop
	bellActivator = False
	print('[*] Stopping Program...')
	print('[*] Done. Pres Enter to stop...\n\n')