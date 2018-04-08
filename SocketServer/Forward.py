import json


# function from forwarding request to the lock device.
# taking parameter request, lock connection object, phone connection object.
def request_forward(request_to_forward, email, connection, phone_connection):
	# creating request
	request = {}
	request['request'] = request_to_forward
	request['email'] = email
	request['message'] = ''
	# converting to JSON object
	json_request = json.dumps(request)

	# sending to the request.
	try:
		connection.sendall(str.encode(json_request))
		# sending reply to phone.
		phone_connection.sendall(str.encode(request_to_forward+' Done.\n'))
	except Exception as e:
		print('\n[**]  Exception :: Request forward :: ' + str(e))
	finally:
		phone_connection.sendall(str.encode('Not done.\n'))
