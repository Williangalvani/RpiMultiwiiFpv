from messages import *
from serial.tools import list_ports
import os
#from protocol import *
import serial
import time
import signal
import threading

class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args

        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


class TelemetryReader():

    def __init__(self):
        print "instantiating class"
        self.run = True
        self.thread = FuncThread(self.loop)
        self.thread.start()
        self.attitude = [0, 0, 0]
        self.buffer = ""
        self.ser = None

    def loop(self):
        print "starting loop"
        while self.run:
            print "inside loop"
            try:
                self.ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1)
                self.ser.flushInput()
                self.connected = True
                print "connected"
            except Exception, e:
                print "could not connect, retrying in 3s\n", e
                time.sleep(3)
            if self.connected:
                try:
                    while self.run:
                            self.attitude = self.read_attitude()
                            # print self.attitude
                            #self.window.set_attitude(*self.attitude)
                            time.sleep(0.05)
                except Exception, e:
                    print e

    def stop(self):
        self.run = False


    # def list_serial_ports(self):
    #     # Windows
    #     if os.name == 'nt':
    #         # Scan for available ports.
    #         available = []
    #         for i in range(256):
    #             try:
    #                 s = serial.Serial(i)
    #                 available.append('COM'+str(i + 1))
    #                 s.close()
    #             except serial.SerialException:
    #                 pass
    #         return available
    #     else:
    #         # Mac / Linux
    #         print [port[0] for port in list_ports.comports ()]
    #         return [port[0] for port in list_ports.comports ()]

    def receiveAnswer(self, expectedCommand):
        time.sleep(0.001)
        command = None
        size = 0
        while command != expectedCommand:
            if len(self.buffer) > 15:
                self.buffer = "$M>" + self.buffer.rsplit("$M>", 1)[-1]
            header = "000"
            #print self.buffer
            while "$M>" not in header:
                #print "waiting header", header
                new = ""
                try:
                    new = self.ser.read(1)
                except serial.SerialTimeoutException:
                    print "timeout!"
                    return None
                header += new
                if len(header) > 3:
                    header = header[1:]
            size = ord(self.ser.read())
            command = ord(self.ser.read())
            if command != expectedCommand:
                print "wrong command!"
        data = []
        for i in range(size):
            data.append(ord(self.ser.read()))
        checksum = 0
        checksum ^= size
        checksum ^= command
        for i in data:
            checksum ^= i
        receivedChecksum = ord(self.ser.read())
        #print 'command' , command
        #print 'size' , size
        #print 'data' , data
        #print checksum, receivedChecksum
        if command != expectedCommand:
            print( "commands dont match!", command, expectedCommand, len(self.buffer))
            if receivedChecksum == checksum:          # was not supposed to arrive now, but data is data!
                #self.try_handle_response(command,data)
                #print "gotcha"
                #self.flush_input()
                pass
            return None
        if checksum == receivedChecksum:
            #print data
            return data
        else:
            print ('lost packet!')
            return None

    def MSPquery(self, command):
            #self.ser.flushInput()
            o = bytearray('$M<')
            #print dir(o)
            c = 0
            o += chr(0)
            c ^= o[3]       #no payload
            o += chr(command)
            c ^= o[4]
            o += chr(c)
            answer = None
            while not answer:
                    #print "writing" , o
                    self.ser.write(o)
                    #self.ser.flushInput()
                    answer = self.receiveAnswer(command)
            #print answer
            return answer

    def decode32(self, data):
        #print data
        result = (data[0] & 0xff) + ((data[1] & 0xff) << 8) + ((data[2] & 0xff) << 16) + ((data[3] & 0xff) << 24)
        is_negative = data[3] >= 128
        if is_negative:
            result -= 2**32
        return result

    def decode16(self, data):
        #print data
        result = (data[0] & 0xff) + ((data[1] & 0xff) << 8)
        is_negative = data[1] >= 128
        if is_negative:
            result -= 2**16
        return result


    def read_gps(self):
        print "requesting gps"
        answer = self.MSPquery(MSP_RAW_GPS)
        if answer:
            lat_list = answer[2:6]
            long_list = answer[6:10]
            latitude = self.decode32(lat_list)/10000000.0
            longitude = self.decode32(long_list)/10000000.0
            #print longitude,latitude
            return longitude, latitude
        return (0,0)

    def read_attitude(self):
        #print "requesting attitude"
        answer = self.MSPquery(MSP_ATTITUDE)
        if answer:
            #print answer
            roll = self.decode16(answer[0:2])/10.0
            pitch = self.decode16(answer[2:4])/10.0
            mag = self.decode16(answer[4:6])
            #print roll,pitch
            return roll, pitch, mag
        return 0, 0, 0

reader = None


# reader = TelemetryReader()
# time.sleep(10)
