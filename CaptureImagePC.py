# importing module.
import time
import cv2 as cv
import os


def capture():
    print("[*] Checking path...\n")

    # Creation of ProgramData folder to store images and file number.
    if not os.path.exists('ProgramData'):
        os.makedirs('ProgramData')

    # checking the numberFile exist or not !! if not then create the file.
    if not os.path.exists('ProgramData/numberFile'):
        numberFile = open(os.path.join('ProgramData', 'numberFile'), 'w')
        numberFile.close()

    # filename and extention.
    image = 'imgCL'
    ex = '.png'

    # checking the file size.
    if os.stat('ProgramData/numberFile').st_size == 0:
        # when the file size is 0 the the 1st execution of this file.
        # So open the file in write mode.
        # And write 0 for first time.
        numberFile = open('ProgramData/numberFile', 'w')
        numberFile.write('0')
        numberFile.close()
        # take the file number for file name creation.
        number = '0'
    else:
        # if the file size is not empty.
        # read the file and convert it into int.
        numberFile = int(open('ProgramData/numberFile', 'r').read())

        # increased value for the next file number.
        numberFile += 1

        # convert to string and write into the file.
        number = str(numberFile)
        numberFile = open('ProgramData/numberFile', 'w')
        numberFile.write(number)
        numberFile.close()

    print("[*] Generating file name...\n")
    # genereting the name by joining name file number and extention.
    # imgCl30.jpg
    name = image + number + ex

    print("[*] Capturing image...\n")
    # creating object of opencv
    camera = cv.VideoCapture(0)

    # wait for turning the camera on.
    time.sleep(2)

    # capture the image from camera.
    _, img = camera.read()

    # saving the image.
    print("Saving image...")
    cv.imwrite(os.path.join('ProgramData', name), img)

    # delete the camera object
    del (camera)

    # showing the image.
    cv.imshow('Captured', img)
    cv.waitKey(500)
    cv.destroyAllWindows()
