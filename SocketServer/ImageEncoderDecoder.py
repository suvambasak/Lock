import base64


# Encoding image.
# Take image path as parameter.
def encode(imageFilePath):
    try:
        # open the image file.
        with open(imageFilePath, 'rb') as image:
            # encode image.
            encodedImage = base64.b64encode(image.read())

            # encoded filename
            encodedFileName = imageFilePath.split('.')
            encodedFileName = encodedFileName[0]

            print('[*] Encoded File name  :: ' + encodedFileName)

            # write the encoded content into the file.
            with open(encodedFileName, 'wb') as encodedFile:
                encodedFile.write(encodedImage)
                encodedFile.close()
            print('[||] Encoding complete :: ' + encodedFileName)
            return encodedFileName
    except Exception as e:
        print('[*] Exception in encode :: ' + str(e))


# Decoding Image.
# Take Encoded file path as parameter.
def decode(EncodedImagePath):
    # computer the image file name with path.
    decodedImagePath = EncodedImagePath + '.png'
    try:
        # read the encoded image file.
        encodedImage = open(EncodedImagePath, 'rb').read()

        # decode the encoded image file.
        image = base64.b64decode(encodedImage)

        # open a file with the image filename and write the decoded file content.
        with open(decodedImagePath, 'wb') as imageFile:
            imageFile.write(image)
            imageFile.close()

        print('[||] Decoding complete :: ' + decodedImagePath)
    except Exception as e:
        print('[*] Exception decode :: ' + str(e))


        # decode('ServerBackup/basak/imgCL5')
