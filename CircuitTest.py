import RPi.GPIO as GPIO
import picamera
import time

LED = 19
BUTTON = 26
TRIG = 6
ECHO = 13
ControlPin = [4, 17, 27, 22]

GPIO.setmode(GPIO.BCM)


print ('####### Check Pin Numbers #########')
print ('LED : ',LED)
print ('Button : ',BUTTON)
print ('Trigger : ',TRIG)
print ('Echo : ',ECHO)
print ('Stepper Control Pin : ',str(ControlPin))
print ('---------------------------')
print ('Press Enter to continue..')
input()

# Camera test function.
def test_camera():
	print('------------ Pi Camera Test --------------')
	camera = picamera.PiCamera()
	try:
		camera.capture('../CameraTest.png')
	except Exception as e:
		print ('[*] Exception :: '+str(e))
	finally:
		camera.close()


# LED Test function.
def test_LED():
	print ('------------ LED Test --------------')

	GPIO.setup(LED,GPIO.OUT)

	print ("LED ON")
	GPIO.output(LED,GPIO.HIGH)

	for i in range(0,3):
		print (i,'second')
		time.sleep(1)

	print ("LED OFF")
	GPIO.output(LED,GPIO.LOW)


# Button Test function.
def test_button():
	print ('---------- Button Test -----------')

	GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	push = 0

	try:
		while push < 3:
			if GPIO.input(26) == True:
				push+=1
				print ("Push :: ",push)
			time.sleep(0.3)
	except Exception as e:
		print ('[*] Exception ::'+str(e))


# Distance Test function.
def test_distance():
	print ('--------- Distance Test ---------')

	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)

	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)

	while GPIO.input(ECHO) == False:
		start = time.time()
	while GPIO.input(ECHO) == True:
		end = time.time()

	try:
		sig_time = end-start

		distance = sig_time / 0.000058
		print ('\nDistance : {} cm'.format(distance))

		distance = sig_time / 0.000148
		print ('Distance : {} inch'.format(distance))
	except Exception as e:
		print ('[**] Exception :: '+str(e))

# Stepper test function.
def test_stepper():
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

	print ('90 Degree Clockwise...')

	for i in range(128):
		print ('STEP::',i)
		# Go through the sequence once
		for halfstep in range(8):
			# Go through each half-step
			for pin in range(4):
				# Set each pin
				GPIO.output(ControlPin[pin], forward[halfstep][pin])
			time.sleep(0.001)

	print('90 Degree Anti-Clockwise...')

	for i in range(128):
		print('STEP::', i)
		# Go through the sequence once
		for halfstep in range(8):
			# Go through each half-step
			for pin in range(4):
				# Set each pin
				GPIO.output(ControlPin[pin], backward[halfstep][pin])
			time.sleep(0.001)


try:
	req = input('Test All Componemts (y/n) : ')
	if req == 'y' or req == 'Y':
		print ('\n'*3)
		print ('Starting All Test.')

		print('\n' * 3)
		test_camera()

		print ('\n'*3)
		test_LED()

		print('\n' * 3)
		test_button()

		print('\n' * 3)
		test_distance()

		print('\n' * 3)
		test_stepper()
	elif req == 'n' or req == 'N':
		counter = True
		while counter:
			print ('\n\nSelect Component\n\n')
			print ('LED ::> 1')
			print('Button ::> 2')
			print('HC-SRO4 ::> 3')
			print('Pi-Camera ::> 4')
			print ('Stepper (28BJY-48) ::> 5')
			print('EXIT ::> 0')

			selection = int(input('\n Your Selection : '))

			if selection == 1:
				test_LED()
			elif selection == 2:
				test_button()
			elif selection == 3:
				test_distance()
			elif selection == 4:
				test_camera()
			elif selection == 5:
				test_stepper()
			elif selection == 0:
				counter = False
			else:
				print ('Select Again')
	else:
		print ('Exit.')

except Exception as e:
	print ('[*] Exception :: '+str(e))
finally:
	GPIO.cleanup()