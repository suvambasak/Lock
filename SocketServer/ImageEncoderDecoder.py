import base64


# Encoding image.
# Take image path as parameter.
def encode(image_file_path):
	try:
		# open the image file.
		with open(image_file_path, 'rb') as image:
			# encode image.
			encoded_image = base64.b64encode(image.read())

			# encoded filename
			encoded_file_name = image_file_path.split('.')
			encoded_file_name = encoded_file_name[0]

			print('[*] Encoded File name  :: ' + encoded_file_name)

			# write the encoded content into the file.
			with open(encoded_file_name, 'wb') as encoded_file:
				encoded_file.write(encoded_image)
				encoded_file.close()
			print('[||] Encoding complete :: ' + encoded_file_name)
			return encoded_file_name
	except Exception as e:
		print('[*] Exception in encode :: ' + str(e))


# Decoding Image.
# Take Encoded file path as parameter.
def decode(encoded_image_path):
	# computer the image file name with path.
	decoded_image_path = encoded_image_path + '.png'
	try:
		# read the encoded image file.
		encoded_image = open(encoded_image_path, 'rb').read()

		# decode the encoded image file.
		image = base64.b64decode(encoded_image)

		# open a file with the image filename and write the decoded file content.
		with open(encoded_image_path, 'wb') as image_file:
			image_file.write(image)
			image_file.close()

		print('[||] Decoding complete :: ' + encoded_image_path)
	except Exception as e:
		print('[*] Exception decode :: ' + str(e))

		# decode('ServerBackup/basak/imgCL5')
