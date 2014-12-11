__author__ = 'will'


import socket
import os
import subprocess
import time
import threading
import signal

import cPickle as pkl
from protocol.messages import *

class Sender(threading.Thread):

    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.addr = (ip, 21567)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.msg_counter = 0

        self.requested = [] # special messages on request
        self.periodic = [(RPI_COUNTER, self.counter),
                         (MSP_SET_RAW_RC, self.get_rc),
                         (MSP_PID, [])]  # regular messages, sent one each cycle

        self.len_periodics = len(self.periodic)


    def counter(self):
        self.msg_counter += 1
        return self.msg_counter

    def get_rc(self):
        return [1500 for i in range(8)]


    def get_next_message(self):
        """
        :return: next data message to be sent
        """
        if self.requested:
            name, lista = self.requested.pop(0)
            op = "req"
        else:
            name, lista = self.periodic[self.msg_counter % self.len_periodics]
            op = "per"
        try:
            lista = lista()
        except:
            pass
        dict = {str(name): lista}
        data = "{0} >{1}".format(op,pkl.dumps(dict))
        return data

    def run(self):
        while self.running:
            time.sleep(0.01)
            data = self.get_next_message()
            self.msg_counter += 1
            self.sock.sendto(data, self.addr)
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
        if string.startswith("att"):
            #print "got attitude", string
            self.data['attitude'] = pkl.loads(string.split(">", 1)[1])

        elif string.startswith("rssi"):
            self.data['RSSI'] = pkl.loads(string.split(">", 1)[1])
        else:
            print string


    def get(self, key):
        if key in self.data:
            return self.data[key]
        else:
            return None

    def stop(self):
        print "trying to finalize ground receiver"
        self.running = False
