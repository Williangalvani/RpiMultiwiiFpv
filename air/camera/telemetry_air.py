__author__ = 'will'

import socket
import os
import subprocess


print "opening socket..."
UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen_addr = ("",21567)
UDPSock.bind(listen_addr)
print "Socket open, waiting for connection"

done = False
stream = False
while not done:
        data, addr = UDPSock.recvfrom(1024)
        print data.strip(), addr
        if not stream:
            try:
                print "opening video stream."
                subprocess.Popen(["sh", "cameraGst.sh", "{0}".format(addr[0])])
                print "video stream open."
                stream = True
            except:
                pass