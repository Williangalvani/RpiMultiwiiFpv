import socket
import subprocess
import signal
import threading
import time
import cPickle as pkl
from serialcomm.seriallink import TelemetryReader
from rssi import read_rssi
from protocol.messages import *
import os
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
        self.request = []

    def run(self):
        msg_counter = 1
        while self.running:
            if self.receiver.addr:
                if not self.addr:
                    self.addr = (self.receiver.addr, 21567)

                if not len(self.request):
                    time.sleep(0.01)

                if self.request:
                    request = self.request.pop(0)
                    datadict = {request[0]:request[1]}
                    data = "resp >{0}".format(pkl.dumps(datadict))
                else:
                    if msg_counter % 5 == 0:
                        data = "stat >{0}".format(pkl.dumps(self.serial.status_flags))
                    else:
                        data = "att >{0}".format(pkl.dumps(self.serial.attitude))
                    msg_counter += 1

                self.sock.sendto(data, (self.receiver.addr, 21567))

                if msg_counter % 50 == 0:
                    data = "rssi >{0}".format(pkl.dumps(read_rssi()))
                    self.sock.sendto(data, (self.receiver.addr, 21567))
            else:
                time.sleep(0.5)

        print "Air sender thread finalized!"

    def stop(self):
        print "trying to stop air sender thread..."
        self.running = False

    def queue(self, msg, data):
        self.request.append((msg, data))


class Receiver(threading.Thread):

    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_address = ("", 21567)
        self.sock.bind(listen_address)
        self.running = True
        self.stream = False
        self.addr = None
        self.setDaemon(True)
        self.data = {}
        self.serial = serial

    def run(self):
        while self.running:
                data, addr = self.sock.recvfrom(1024)
                self.addr = addr[0]
                time.sleep(0.01)
                self.treat_data(data)

        print "air receiver finalized!"

    def treat_data(self, string):
        data = None
        if string.startswith("req"):
            data = pkl.loads(string.split(">", 1)[1])
        elif string.startswith("per"):
            data = pkl.loads(string.split(">", 1)[1])
        else:
            print "unknown message:", string

        if str(RPI_COUNTER) in data:
            pass
        elif str(MSP_SET_RAW_RC) in data:
            self.serial.queue_rc(data[str(MSP_SET_RAW_RC)])
        elif str(MSP_PID) in data:
            self.serial.queue_pid_request()
        elif str(MSP_SET_PID) in data:
            self.serial.queue_pid_write(data[str(MSP_SET_PID)])
        elif str(MSP_EEPROM_WRITE) in data:
            self.serial.queue_eeprom()
        elif str(MSP_BOX) in data:
            self.serial.queue(MSP_BOX)
        elif str(MSP_SET_BOX) in data:
            payload = []
            boxes = data[str(MSP_SET_BOX)]
            for name in self.serial.box_names:
                number = 0
                for index, value in enumerate(boxes[name]):
                    number += (1 if value else 0) << index
                payload.append(number)

            self.serial.queue_set_box(payload)
        else:
            print "unknown data: ", data

    def stop(self):
        print "trying to stop air receiver..."
        self.running = False

