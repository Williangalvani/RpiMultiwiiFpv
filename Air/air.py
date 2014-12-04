__author__ = 'will'

import socket
import subprocess
import signal
import threading
import time
import cPickle as pkl
from serialcomm.seriallink import TelemetryReader
from rssi import read_rssi

print "Socket open, waiting for connection"


done = False

class Sender(threading.Thread):
    def __init__(self, serial, receiver):
        threading.Thread.__init__(self)
        self.serial = serial
        self.receiver = receiver
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.addr = None
        self.setDaemon(True)

    def run(self):
        msg_counter = 1
        while self.running:
            if self.receiver.addr:
                if not self.addr:
                    self.addr = (self.receiver.addr, 21567)

                time.sleep(0.01)
                data = "att >{0}".format(pkl.dumps(self.serial.attitude))
                msg_counter += 1
                self.sock.sendto(data, (self.receiver.addr, 21567))

                if msg_counter % 50 == 0:
                    data = "rssi >{0}".format(pkl.dumps(read_rssi()))


        print "air sender finalized!"

    def stop(self):
        print "trying to stop air sender..."
        self.running = False


class Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_addr = ("", 21567)
        self.sock.bind(listen_addr)
        self.running = True
        self.stream = False
        self.addr = None
        self.setDaemon(True)

    def run(self):
        while self.running:
                data, addr = self.sock.recvfrom(1024)
                self.addr = addr[0]
                time.sleep(0.01)
                # print data.strip(), addr
                # UDPSock.sendto("{0}".format(reader.attitude), (addr[0], 21567))
                if not self.stream:
                    try:
                        print "opening video stream."
                        subprocess.Popen(["sh", "cameraGst.sh", "{0}".format(addr[0])])
                        print "video stream open."
                        self.stream = True
                    except:
                        pass
        print "air receiver finalized!"

    def stop(self):
        print "trying to stop air receiver..."
        self.running = False

reader = TelemetryReader()
receiver = Receiver()
receiver.start()
sender = Sender(reader, receiver)
sender.start()


def exit_gracefully(signum, frame):
    print "trying to stop threads..."
    reader.stop()
    # receiver.stop()
    # sender.stop()
    # receiver.join()
    # sender.join()
    # global done
    exit()
    done = True

signal.signal(signal.SIGINT, exit_gracefully)

while not done:
    time.sleep(1)
