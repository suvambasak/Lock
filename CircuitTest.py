import RPi.GPIO as GPIO
import time

LED = 19
BUTTON = 26
TRIG = 6
ECHO = 13

GPIO.setmode(GPIO.BCM)


print ('####### Check Pin Numbers #########')
print ('LED : ',LED)
print ('Button : ',BUTTON)
print ('Trigger : ',TRIG)
print ('Echo : ',ECHO)
print ('---------------------------')
print ('Press Enter to continue..')
input()

## LED Test function.
def test_LED():
	print ('------------LED Test--------------')
	GPIO.setup(LED,GPIO.OUT)
	print ("LED ON")
	GPIO.output(LED,GPIO.HIGH)
	for i in range(0,3):
		time.sleep(1)
	print ("LED OFF")
	GPIO.output(LED,GPIO.LOW)

## Button Test function.
def test_button():
	print ('----------Button Test-----------')
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

## Distance Test function.
def test_distance():
	print ('---------Distance Test-------')
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
		print ('Distance : {} inchs'.format(distance))

	except Exception as e:
		print ('[**] Exception :: '+str(e))

try:
	test_distance()
except Exception as e:
	print ('[*] Exception :: '+str(e))
finally:
	GPIO.cleanup()