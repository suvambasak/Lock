import pymysql


class Database:
	"""Database connection and functions"""

	def __init__(self):
		self.rootPath = "/home/suvam/PycharmProjects/Lock/SocketServer/"
		self.host = 'localhost'
		self.user = 'root'
		self.password = ''
		self.dbname = 'lockdb'
		try:
			self.db = pymysql.connect(self.host, self.user, self.password, self.dbname)
			print("[*] Database Connected.")
		except Exception as e:
			print("\n\n[**] Exception :: Database.py __init__ :: " + str(e))
			print('\n\n')
		self.db.autocommit(True)
		self.cursor = self.db.cursor()

	# submit the notification into database
	def submit_notify(self, username, email_id, notify_text, image_id):
		try:
			sql = "INSERT INTO `notification` (`id`, `username`, `email`, `notifyText`, `imageId`) VALUES (NULL, '%s', '%s', '%s', '%s');" % (
				username, email_id, notify_text, image_id)
			self.cursor.execute(sql)
		# auto commit
		except Exception as e:
			print('\n[**] Exception :: submitNotify :: ' + str(e))

	# function for inserting online Device List
	def insert_online_device(self, username):
		try:
			sql = "INSERT INTO `onlinelist` (`id`, `username`) VALUES (NULL, '%s');" % (username,)
			self.cursor.execute(sql)
		except Exception as e:
			print('\n[**] Database :: insertOnlineDevice :: ' + str(e))

	# delete online Device
	def delete_online_device(self, username):
		try:
			sql = "DELETE FROM onlinelist WHERE username = '%s';" % (username,)
			self.cursor.execute(sql)
		# auto commit
		except Exception as e:
			print('\n[**] Database :: deleteOnlineDevice :: ' + str(e))

	# delete all online Device
	def delete_all_online_device(self):
		try:
			sql = "TRUNCATE TABLE `onlinelist`"
			self.cursor.execute(sql)
			print('[*] Online List Cleared.\n')
		# auto commit
		except Exception as e:
			print('\n[**] Database :: deleteOnlineDevice :: ' + str(e))

	# function for inserting imageBackup
	def insert_image_backup(self, username, path):
		try:
			path = self.rootPath + path
			sql = "INSERT INTO `imagebackup` (`id`, `username`, `path`) VALUES (NULL, '%s', '%s');" % (username, path)
			self.cursor.execute(sql)
			# auto commit
			sql = "SELECT id FROM `imagebackup` WHERE path = '%s'" % (path,)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: insertImageBackup :: ' + str(e))

	# function for checking android ID.
	def user_authentication(self, username, android_id, email):
		try:
			if self.check_androidid_id(email, android_id) and self.check_permission(email, username):
				return True
			else:
				return False
		except Exception as e:
			print('\n[**] Database :: user_authentication :: ' + str(e))
			return False

	def check_androidid_id(self, email, android_id):
		try:
			sql = "SELECT id FROM `owner` WHERE android_id = '%s' AND email = '%s'" % (android_id, email)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: check_androidid_id :: ' + str(e))
			return 0

	def check_permission(self, email, username):
		try:
			sql = "SELECT COUNT(*) FROM `access` WHERE username = '%s' AND email = '%s' AND enable = 'Y'" % (
			username, email)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			if result[0][0] == 0:
				print('\n\n[**] permission Denied.')
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: check_permission :: ' + str(e))
			return 0

	# function for checking lock MAC.
	def check_lock_mac(self, username, lock_mac):
		try:
			sql = "SELECT id FROM device WHERE username  = '%s' AND lock_mac = '%s'" % (username, lock_mac)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: checkLockMAC :: ' + str(e))
			return 0

	# function for getting email address.
	def get_email_address(self, username):
		try:
			sql = "SELECT owner_email FROM `device` WHERE username = '%s'" % username
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: getEmailAddress :: ' + str(e))
			return 0

	def get_owner_name(self, username):
		try:
			sql = "SELECT owner.name FROM `device`, `owner` WHERE device.username = '%s' AND device.owner_email = owner.email" % username
			self.cursor.execute(sql)
			# fetch data.
			result = self.cursor.fetchall()
			# return 1st data.
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: getOnwerName :: ' + str(e))
			return 0
