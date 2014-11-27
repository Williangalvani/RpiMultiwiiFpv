__author__ = 'will'


import socket
import os
import subprocess
import time
import threading
import signal

subprocess.Popen(["sh", "viewerGstPC.sh"])
addr = ("192.168.42.1", 21567)

# Simply set up a target address and port ...

class Sender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True

    def run(self):
        msg_counter = 1
        while self.running:
            time.sleep(0.01)
            data = "msg {0}".format(msg_counter)
            #print data
            msg_counter += 1
            self.sock.sendto(data, addr)
        print "ground sender finalized!"

    def stop(self):
        print "trying to finalize ground sender..."
        self.running = False


class Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_addr = ("", 21567)
        self.sock.bind(listen_addr)
        #self.sock.setblocking(0)
        self.running = True

    def run(self):
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            print "received:", data.strip(), addr
        print "finalized ground receiver"

    def stop(self):
        print "trying to finalize ground receiver"
        self.running = False

sender = Sender()
receiver = Receiver()
sender.start()
receiver.start()
run = True

def exit_gracefully(signum, frame):
    print "trying to stop"
    global run
    run = False
    sender.stop()
    receiver.stop()
    sender.join()
    receiver.join()

signal.signal(signal.SIGINT, exit_gracefully)

while run:
    time.sleep(1)