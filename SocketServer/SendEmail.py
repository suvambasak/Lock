# importing packages.
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
import Database as db
import os


# email sending function.
def send(email, msg):
	try:
		# connecting to SMTP
		s = smtplib.SMTP("smtp.gmail.com", 587)
		s.ehlo()
		s.starttls()
		s.ehlo()

		# reading password.
		pwd = open('pwd.pem','r').read()

		# logging in.
		s.login('tech.codebox@gmail.com', pwd)
		print("[*] Logged in...\n")
		print("[*] Sending mail...\n")

		# send mail.
		s.sendmail('tech.codebox@gmail.com', email, msg.as_string())
		s.quit()

		print('Mail Done !!')
	except Exception as e:
		print('\n[**] SendEmail :: send ' + str(e))


# email for disconnect lock.
def disconnect_alert(username):
	try:
		database = db.Database()
		# getting email address and name.
		name = str(database.get_owner_name(username))
		email = str(database.get_email_address(username))

		# content of email.
		content = 'Dear owner ' + name + ',\n\n\t Your locked device seems to have gone offline. Please reconnect to enable lock.'
		print("\n[*] COMPOSING mail...\n")

		# feeling up.
		msg = MIMEMultipart()
		msg['Subject'] = 'Alert'
		msg['From'] = 'tech.codebox@gmail.com'
		msg['To'] = email
		msg.attach(MIMEText(content))

		return send(email, msg)
	except Exception as e:
		print('\n[**] SendEmail :: disconnectAlert ' + str(e))


# email for sending image.
def send_image(username, path):
	try:
		database = db.Database()
		email = str(database.get_email_address(username))
		image = open(path, 'rb').read()

		msg = MIMEMultipart()
		msg['Subject'] = 'Alert'
		msg['From'] = 'tech.codebox@gmail.com'
		msg['To'] = email

		msg.attach(MIMEText("Do you know him/her ?"))
		msg.attach(MIMEImage(image, name=os.path.basename(path)))

		return send(email, msg)

	except Exception as e:
		print('\n[**] SendEmail :: sendImage ' + str(e))

		# sendImage('basak','ServerBackup/basak/imgCL13.jpg')
		# disconnectAlert('basak')
