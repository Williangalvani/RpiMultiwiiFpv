__author__ = 'will'

import socket
import os
import subprocess
from serialcomm.seriallink import TelemetryReader
import signal
import threading
import time


print "Socket open, waiting for connection"


done = False


class Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_addr = ("", 21567)
        self.sock.bind(listen_addr)
        self.running = True
        self.stream = False

    def run(self):
        while self.running:
                data, addr = self.sock.recvfrom(1024)
                print data.strip(), addr
                # UDPSock.sendto("{0}".format(reader.attitude), (addr[0], 21567))
                if not self.stream:
                    try:
                        print "opening video stream."
                        subprocess.Popen(["sh", "cameraGst.sh", "{0}".format(addr[0])])
                        print "video stream open."
                        self.stream = True
                    except:
                        pass

    def stop(self):
        self.running = False

reader = TelemetryReader()
receiver = Receiver()
receiver.start()

def exit_gracefully(signum, frame):
    print "trying to stop"
    reader.stop()
    receiver.stop()
    receiver.join()
    global done
    done = True

signal.signal(signal.SIGINT, exit_gracefully)

while not done:
    time.sleep(1)
