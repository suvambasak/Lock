import MAC as physicalAddress
import socket
import threading
import json
import time
import sys
import FileName
import picamera
import RPi.GPIO as GPIO
import urllib.request

# Distance Function.
def get_distance():
	global Trigger, Echo

	# Issue a singal out.
	GPIO.output(Trigger, True)
	time.sleep(0.00001)
	GPIO.output(Trigger, False)

	while GPIO.input(Echo) == False:
		start = time.time()

	# Get the echo back of the signal. and calculate the time duration.
	while GPIO.input(Echo) == True:
		end = time.time()

	try:
		sig_time = end - start
		# Distance in Inches
		distance = sig_time / 0.000148

		return round(distance)
	except Exception as e:
		print('[*] Exception :: get_distance :: ' + str(e))
		return 100


# Send image function.
# parameter Email, Bell
def send_image(email_id, email=False, bell=False):
	global host, username

	try:
		# retrive the file name.
		number = str(open('ProgramData/numberFile', 'r').read())
		name = 'imgCL' + number + '.png'

		# creating filename & username JSON object.
		filename = {}
		filename['name'] = name
		filename['username'] = username
		filename['emailId'] = email_id

		if email:
			filename['email'] = 'YES'
			filename['bell'] = 'NO'
		elif bell:
			filename['email'] = 'NO'
			filename['bell'] = 'YES'
		else:
			filename['email'] = 'NO'
			filename['bell'] = 'NO'

		json_filename = json.dumps(filename)

		# creating socket object.
		backup_server = socket.socket()

		# connecting to the backup server.
		backup_server.connect((host, 9999))
		# send the JSON objet containing filename and username.
		backup_server.send(str.encode(json_filename))
		time.sleep(2)

		# path to the file.
		# and read the file content
		path = 'ProgramData/' + name
		file = open(path, 'rb')
		file_content = file.read(2048)

		# send the file content until complete.
		while file_content:
			backup_server.send(file_content)
			file_content = file.read(2048)
		file.close()

		backup_server.close()

	except Exception as e:
		print('[*] Exception :: Image send :: ' + str(e))


# Take image function.
def take_image(email_id, email=False):
	# initilizing global variables
	global cameraLock, host, username, camera
	print('\n[||] Email :: ' + str(email))
	# locking the camera to prevent another thread to use camera.
	cameraLock.acquire()

	try:
		new_filename = 'ProgramData/' + FileName.get_filename()
		camera.capture(new_filename)

		# checking for email request ot Take image request.
		if email:
			send_image(email_id, email=True)
		else:
			send_image(email_id)

	except Exception as e:
		print('[**] Exception :: Take Image function :: ' + str(e))

	finally:
		print('[*] Done')
		# releasing the lock when execution of the method complete.
		cameraLock.release()
		print('\n-' * 5)


# Count down function.
def start_count_down():
	global callingBellPressed, cameraLock
	print('[*] Count down start.')

	for i in range(0, 6):
		# Wait for 6 second.
		time.sleep(1)
		current_distance = get_distance()

		# When the object moved from door.
		if current_distance > MIN_DISTANCE:
			print("[*] Exit from count down.")
			return
		print('Object now at {} second ::: {} inch'.format(i, current_distance))

	# Check the person pressed the bell or not.
	if not callingBellPressed:
		cameraLock.acquire()

		# Take Picture and upload to the server.
		try:
			print("[*] Taking picture of SPY.")

			new_filename = 'ProgramData/' + FileName.get_filename()
			camera.capture(new_filename)

			time.sleep(1)

			# sending the image.
			print("[*] Sending SPY Image")
			send_image(None, bell=True)

		except Exception as e:
			print('[**] Exception :: start_count_down :: ' + str(e))
		finally:
			cameraLock.release()


# Thread for HC-SRO4.
# Monitor for object in front of door.
def keep_safe_distance():
	global sensorThreadStatus, callingBellPressed

	# Run until main Thread ends. Check distance in each 1 second.
	while sensorThreadStatus:
		try:
			current_distance = get_distance()

			# If person is not in safe distance call start_count_down.
			if current_distance < MIN_DISTANCE:
				print('Object Detected at : {} inch'.format(current_distance))
				start_count_down()

			# If person moved away the reset the calling bell.
			elif current_distance > MAX_DISTANCE and callingBellPressed:
				callingBellPressed = False
				print("[*] Calling Bell Presss :: Reset")
			time.sleep(1)

		except Exception as e:
			print('[*] Exception :: keep_safe_distance :: ' + str(e))
			time.sleep(5)


# calling Bell Event
def calling_bell():
	# global variable of camera lock and
	global cameraLock, bellActivator, host, username, callingBellPressed

	while bellActivator:
		if GPIO.input(Button) == True:
			print('[*] Calling Bell pressed.')

			# It stops distance sensor thread to take image and upload into the server while calling bell pressed.
			callingBellPressed = True
			cameraLock.acquire()

			try:
				# get the file name for saving new image.
				new_filename = 'ProgramData/' + FileName.get_filename()
				# capture image using Pi camera.
				camera.capture(new_filename)
				time.sleep(0.5)

				# sending the image.
				send_image(None, bell=True)
				print('complete')

			except Exception as e:
				print('[**] Exception :: calling_bell :: ' + str(e))
			finally:
				cameraLock.release()


def fetch_server_ip():
	try:
		print("[**]  Fetching IP Address.")
		print("Please Wait...")

		resp = urllib.request.urlopen('https://techcodebox.000webhostapp.com/lock/server_config.txt')
		ip = resp.read().decode().split()[0]
		return ip
	except Exception as e:
		print('[**] Exception :: fetch_server_ip :: ' + str(e))


# 1 revolution = 8 cycle.
# gear reduction = 1/64.
# 8*64 = 512 cycle for 1 revolution.

def door_locker(control):
	global ControlPin, lockUnlockRequestIgnore
	lockUnlockRequestIgnore = False

	forward = [[1, 0, 0, 0],
			   [1, 1, 0, 0],
			   [0, 1, 0, 0],
			   [0, 1, 1, 0],
			   [0, 0, 1, 0],
			   [0, 0, 1, 1],
			   [0, 0, 0, 1],
			   [1, 0, 0, 1]]

	backward = [[0, 0, 0, 1],
				[0, 0, 1, 1],
				[0, 0, 1, 0],
				[0, 1, 1, 0],
				[0, 1, 0, 0],
				[1, 1, 0, 0],
				[1, 0, 0, 0],
				[1, 0, 0, 1]]
	try:
		doorLock.acquire()
		time.sleep(0.3)

		if control == True:
			print('[*] Locking...')

			for i in range(512):
				# Go through the sequence once
				for halfstep in range(8):
					# Go through each half-step
					for pin in range(4):
						# Set each pin
						GPIO.output(ControlPin[pin], forward[halfstep][pin])
					time.sleep(0.001)

			print('[*] Locked.')

		elif control == False:
			print('Un-locking...')

			for i in range(512):
				# Go through the sequence once
				for halfstep in range(8):
					# Go through each half-step
					for pin in range(4):
						# Set each pin
						GPIO.output(ControlPin[pin], backward[halfstep][pin])
					time.sleep(0.001)

			print('[*] Un-locked.')

	except Exception as e:
		print('[**] Exception :: door_locker :: ' + str(e))
	finally:
		lockUnlockRequestIgnore = True
		doorLock.release()


# global veriables.
global username, MAC, host, jsonInfo
global cameraLock, doorLock
global bellActivator, sensorThreadStatus,  callingBellPressed, lockUnlockRequestIgnore
global camera, redLED, Button, Trigger, Echo, ControlPin
global MAX_DISTANCE, MIN_DISTANCE

redLED = 19
Button = 26
Trigger = 6
Echo = 13
ControlPin = [4, 17, 27, 22]

# PIN Setup
GPIO.setmode(GPIO.BCM)

GPIO.setup(redLED, GPIO.OUT)
GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Trigger, GPIO.OUT)
GPIO.setup(Echo, GPIO.IN)

for pin in ControlPin:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)

camera = picamera.PiCamera()
camera.vflip = True

# Setting username MAC address Host IPv4 and post number.
username = 'basak'
MAC = physicalAddress.getMACHash()
host = fetch_server_ip() #str(sys.argv[1])
post = 9000

lockUnlockRequestIgnore = True
bellActivator = True
sensorThreadStatus = True
callingBellPressed = False
MAX_DISTANCE = 40
MIN_DISTANCE = 25
# thread locks || one camera lock || one door lock.
doorLock = threading.Lock()
cameraLock = threading.Lock()

callingBellThread = threading.Thread(target=calling_bell, name="bell")
keepSafeDistanceThread = threading.Thread(target=keep_safe_distance, name="distance")


# creating identity json
info = {}
info['device'] = 'LockDevice'
info['username'] = username
info['mac'] = MAC
json_info = json.dumps(info)

# socket object.
device = socket.socket()

# connecting to main server
try:
	device.connect((host, post))
	device.send(str.encode(json_info))
except Exception as e:
	print('[**] Exception :: Connecting to Main server :: ' + str(e))

# off/on try catch block.
try:
	# starting calling bell, safe distance thread.
	callingBellThread.start()
	keepSafeDistanceThread.start()

	# main loop for receiving and replying message/request.
	while True:
		try:
			request = device.recv(1024).decode()
			# loads the JSON.
			request = json.loads(request)
			print(request)

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
			print('Requesting for : LOCK')

			lock_req = threading.Thread(target=door_locker, args=(True), name='functionDoorLocker')
			lock_req.start()

			GPIO.output(redLED, GPIO.LOW)
			print("Red LED :: OFF")

		# Unlock request.
		elif request['request'] == 'Unlock':
			print('Requesting for : UNLOCK')

			unlock_req = threading.Thread(target=door_locker, args=(False), name='functionDoorLocker')
			unlock_req.start()

			GPIO.output(redLED, GPIO.HIGH)
			callingBellPressed = False
			print("Red LED :: ON")

		# TakeImage request.
		elif request['request'] == 'TakeImage':
			print('Requesting for : TAKE IMAGE')

			# creating a thread for take image function.
			takeImageFunction = threading.Thread(target=take_image, args=(request['email'], False),
			                                     name='functionTakeImage')
			takeImageFunction.start()


		# Email request.
		elif request['request'] == 'Email':
			print('Requesting for : EMAIL')
			# creating a thread for Email image.
			emailImageFunction = threading.Thread(target=take_image, args=(request['email'], True),
			                                      name='functionEmailImage')
			emailImageFunction.start()

except KeyboardInterrupt as e:
	print('\n-' * 5)
	print('[*] Connection closing...')

	device.close()
	time.sleep(0.5)

	# stopping all Thread.
	bellActivator = False
	sensorThreadStatus = False
	print('[*] Stopping Program...')

finally:
	camera.close()
	GPIO.cleanup()
