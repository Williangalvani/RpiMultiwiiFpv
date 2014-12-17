__author__ = 'will'

import socket
import time
import threading
import cPickle as pkl
from protocol.messages import *

class Sender(threading.Thread):

    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.rpi_address = (ip, 21567)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.msg_counter = 0

        self.requested = [] # special messages on request
        self.periodic = [(RPI_COUNTER, self.counter),
                         (MSP_SET_RAW_RC, self.get_rc)]  # regular messages, sent one each cycle

        self.len_periodics = len(self.periodic)
        self.controls = None

    def set_controls(self, controls):
        self.controls = controls

    def counter(self):
        print "counter: ", self.msg_counter
        return self.msg_counter

    def get_rc(self):
        print "channels:", self.controls.raw_channels
        return self.controls.raw_channels

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
            self.msg_counter += 1
        try:
            data_dict = {str(name): lista}
            data = "{0} >{1}".format(op, pkl.dumps(data_dict))
        except:
            data_dict = {str(name): lista()}
            data = "{0} >{1}".format(op, pkl.dumps(data_dict))
        return data

    def run(self):
        while self.running:
            time.sleep(0.05)
            data = self.get_next_message()
            self.sock.sendto(data, self.rpi_address)
        print "ground sender finalized!"

    def stop(self):
        print "trying to finalize ground sender..."
        self.running = False

    def queue_message(self, code, data=None):
        self.requested.append([code, data])


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
            self.treat_data(data.strip())
        print "Finalized ground receiver"

    def treat_data(self, string):
        if string.startswith("att"):
            self.data['attitude'] = pkl.loads(string.split(">", 1)[1])
        elif string.startswith("stat"):
            self.data['status'] = pkl.loads(string.split(">", 1)[1])

        elif string.startswith("rssi"):
            self.data['RSSI'] = pkl.loads(string.split(">", 1)[1])
        elif string.startswith("resp"):
            data = pkl.loads(string.split(">", 1)[1])
            if MSP_PID in data:
                self.data['pid'] = data[MSP_PID]
        else:
            print "unknown message:", string

    def get(self, key):
        if key in self.data:
            return self.data[key]
        else:
            return None

    def stop(self):
        print "trying to finalize ground receiver"
        self.running = False
