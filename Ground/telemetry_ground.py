__author__ = 'will'


import socket
import os
import subprocess
import time
import threading
import signal

addr = ("192.168.42.1", 21567)

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
        self.running = True
        self.data = {}

    def run(self):
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            #print "received:", data.strip(), addr
            self.treatData(data.strip())
        print "finalized ground receiver"


    def treatData(self, string):
        if 'att' in string:
            #print "got attitude", string
            self.data['attitude'] = string
        #print self.data

    def stop(self):
        print "trying to finalize ground receiver"
        self.running = False
