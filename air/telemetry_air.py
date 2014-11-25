__author__ = 'will'

import socket
import os

# A UDP server

# Set up a UDP server
UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# Listen on port 21567
# (to all IP addresses on this system)
listen_addr = ("",21567)
UDPSock.bind(listen_addr)

# Report on all data packets received and
# where they came from in each case (as this is
# UDP, each may be from a different source and it's
# up to the server to sort this out!)
done = False
stream = False
while not done:
        data,addr = UDPSock.recvfrom(1024)
        print data.strip(),addr
        if not stream:
            try:
                os.system("cd camera && sh cameraGst.sh {0}&".format(addr[0]))
                stream = True
            except:
                pass