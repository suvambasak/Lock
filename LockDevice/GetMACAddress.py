import MAC as physicalAddress
MAC = physicalAddress.getMACHash()

file = open('MAC','w')
file.write(MAC)
file.close()
print ('MAC :: '+MAC)
print ('Done.')
