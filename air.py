__author__ = 'will'

import signal
import os
import subprocess
import time
from Air.air import Sender, Receiver
from Air.serialcomm.seriallink import TelemetryReader

class Launcher():

    def __init__(self):
        self.reader = TelemetryReader()
        self.receiver = Receiver(self.reader)
        self.receiver.start()
        self.sender = Sender(self.reader, self.receiver)
        self.sender.start()
        self.stream = False
        while True:
            time.sleep(1)
            self.start_stream()

    def start_stream(self):
        if self.receiver.addr and not self.stream:
            addr = self.receiver.addr
            path = os.path.join(os.getcwd(), "Air")
            subprocess.Popen(["sh", "cameraGst.sh", "{0}".format(addr)], cwd = path)
            time.sleep(3)
            self.stream = True

def exit_gracefully(signum, frame):
    exit()

signal.signal(signal.SIGINT, exit_gracefully)

Launcher()
