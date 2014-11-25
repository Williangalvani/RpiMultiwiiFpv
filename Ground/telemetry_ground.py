__author__ = 'will'


import socket
import os
import subprocess
import time
# This is an example of a UDP client - it creates
# a socket and sends data through it

# create the UDP socket
#os.system("sh viewerGstPC.sh&")
subprocess.Popen(["sh", "viewerGstPC.sh"])
UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

data = " jasjlsdfjk sdkldfkjlsd jlksfjklsd\n"

# Simply set up a target address and port ...
addr = ("192.168.42.1", 21567)
# ... and send data out to it!
UDPSock.sendto(data,addr)

while True:
    time.sleep(0.1)
    UDPSock.sendto(data,addr)