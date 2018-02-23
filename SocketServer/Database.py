import pymysql


class Database:
	'''Database connection and functions'''

	def __init__(self):
		self.rootPath = "C:/Users/Suvam Basak/PycharmProjects/Lock/SocketServer/"
		self.host = 'localhost'
		self.user = 'root'
		self.password = ''
		self.dbname = 'lockdb'
		try:
			self.db = pymysql.connect(self.host, self.user, self.password, self.dbname)
			print("[*] Database Connected.")
		except Exception as e:
			print("\n\n[**] Exception :: Database.py __init__ :: " + str(e))
			print ('\n\n')
		self.db.autocommit(True)
		self.cursor = self.db.cursor()

	# submit the notification into database
	def submitNotify(self, username, emailId, notifyText, imageId):
		try:
			sql = "INSERT INTO `notification` (`id`, `username`, `email`, `notifyText`, `imageId`) VALUES (NULL, '%s', '%s', '%s', '%s');" % (
				username, emailId, notifyText, imageId);
			self.cursor.execute(sql)
		# auto commit
		except Exception as e:
			print('\n[**] Exception :: submitNotify :: ' + str(e))

	# function for inserting online Device List
	def insertOnlineDevice(self, username):
		try:
			sql = "INSERT INTO `onlineList` (`id`, `username`) VALUES (NULL, '%s');" % (username,)
			self.cursor.execute(sql)
		except Exception as e:
			print('\n[**] Database :: insertOnlineDevice :: ' + str(e))

	# delete online Device
	def deleteOnlineDevice(self, username):
		try:
			sql = "DELETE FROM onlineList WHERE username = '%s';" % (username,)
			self.cursor.execute(sql)
		# auto commit
		except Exception as e:
			print('\n[**] Database :: deleteOnlineDevice :: ' + str(e))

	# delete all online Device
	def deleteAllOnlineDevice(self):
		try:
			sql = "TRUNCATE TABLE `onlineList`"
			self.cursor.execute(sql)
		# auto commit
		except Exception as e:
			print('\n[**] Database :: deleteOnlineDevice :: ' + str(e))

	# function for inserting imageBackup
	def insertImageBackup(self, username, path):
		try:
			path = self.rootPath + path
			sql = "INSERT INTO `imageBackup` (`id`, `username`, `path`) VALUES (NULL, '%s', '%s');" % (username, path)
			self.cursor.execute(sql)
			# auto commit
			sql = "SELECT id FROM `imageBackup` WHERE path = '%s'" % (path,)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: insertImageBackup :: ' + str(e))

	# function for checking android ID.
	def checkAndroidId(self, username, androidId):
		try:
			sql = "SELECT id FROM device WHERE username = '%s' AND androidId = '%s'" % (username, androidId)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: checkAndroidId :: ' + str(e))
			return 0

	# function for checking member android ID.
	def checkMemberAndroidId(self, username, androidId):
		try:
			sql = "SELECT id FROM `memberDetails` WHERE username = '%s' AND androidId = '%s'" % (
				username, androidId)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: ccheckMemberAndroidId :: ' + str(e))
			return 0

	# function for checking lock MAC.
	def checkLockMAC(self, username, lockMAC):
		try:
			sql = "SELECT id FROM device WHERE username  = '%s' AND lockMac = '%s'" % (username, lockMAC)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: checkLockMAC :: ' + str(e))
			return 0

	# function for getting email address.
	def getEmailAddress(self, username):
		try:
			sql = "SELECT email from owner WHERE username = '%s'" % (username)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: getEmailAddress :: ' + str(e))
			return 0

	# function for getting email address.
	def getEmailAddress(self, username):
		try:
			sql = "SELECT email from owner WHERE username = '%s'" % (username)
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: getEmailAddress :: ' + str(e))
			return 0

	def getOwnerName(self, username):
		try:
			sql = "SELECT name FROM owner WHERE username = '%s'" % (username)
			self.cursor.execute(sql)
			# fetch data.
			result = self.cursor.fetchall()
			# return 1st data.
			return result[0][0]
		except Exception as e:
			print('\n[**] Database :: getOnwerName :: ' + str(e))
			return 0
