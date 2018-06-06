# import FileName
#
# print (FileName.get_filename())
#
# currentDistance = 10
# i = 30
#
# print('Object now at {} second ::: {} inch'.format(i,currentDistance))


'''28BYJ-48 – 5V Stepper Motor s'''

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

ControlPin = [4, 17, 27, 22]

for pin in ControlPin:
	GPIO.setup(pin,GPIO.OUT)
	GPIO.output(pin,0)

# clockwise

# seq = [	[1,0,0,0],
# 		[1,1,0,0],
# 		[0,1,0,0],
# 		[0,1,1,0],
# 		[0,0,1,0],
# 		[0,0,1,1],
# 		[0,0,0,1],
# 		[1,0,0,1]	]

# counter-clockwise
seq = [	[0,0,0,1],
		[0,0,1,1],
		[0,0,1,0],
		[0,1,1,0],
		[0,1,0,0],
		[1,1,0,0],
		[1,0,0,0],
		[1,0,0,1]	]


# 1 revolution = 8 cycle
# gear reduction = 1/64
# 8*64 = 512 cycle for 1 revolution

for i in range(64):
	# Go through the sequence once
	for halfstep in range(8):
		# Go through each half-step
		for pin in range(4):
			# Set each pin
			GPIO.output(ControlPin[pin], seq[halfstep][pin])
		time.sleep(0.001)

GPIO.cleanup()