import json

# function from forwarding request to the lock device.
# taking parameter request, lock connection object, phone connection object.
def requestForward(requestToForward, email, connection, phoneConnection):
    # creating request
    request = {}
    request['request'] = requestToForward
    request['email'] = email
    request['message'] = ''
    # converting to JSON object
    jsonRequest = json.dumps(request)

    # sending to the request.
    try:
        connection.sendall(str.encode(jsonRequest))
        # sending reply to phone.
        phoneConnection.sendall(str.encode('Done.\n'))
    except Exception as e:
        print('\n[**]  Exception :: Request forward :: ' + str(e))
        phoneConnection.sendall(str.encode('Not done.\n'))
