from protocol.messages import *
# from protocol import *
import serial
import time
import threading
import traceback

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
        self.sender = None
        self.requested = []  # special messages on request
        self.periodic = [(self.read_attitude, None),(self.get_status, None) ]  # regular messages, sent one each cycle
        self.periodic_len = len(self.periodic)
        self.msg_counter = 0
        self.pidnames = []
        self.pid_list = []

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
                        if self.requested:
                            function, params = self.requested.pop(0)
                            function(params)

                        else:
                            function, params = self.periodic[self.msg_counter% self.periodic_len]
                            function(params)
                            self.msg_counter += 1
                except Exception, e:
                    print e, "aqui"
                    print traceback.format_exc()

    def stop(self):
        self.run = False

    def set_sender(self, sender):
        self.sender = sender

###### get rid of this!
    def queue_rc(self, rc_list):
        self.requested.append((self.write_rc, rc_list))

    def queue_pid_request(self):
        self.requested.append((self.read_pid, []))

    def write_rc(self, rc_list):
        self.MSPquery16d(MSP_SET_RAW_RC, rc_list)


#############################3

    def receiveAnswer(self, expectedCommand):
        time.sleep(0.0001)
        command = None
        size = 0
        start = time.time()
        while command != expectedCommand:
            #print "waiting command", expectedCommand
            if time.time() > start + 0.5:
                print "timeout"
                return None
            if len(self.buffer) > 15:
                self.buffer = "$M>" + self.buffer.rsplit("$M>", 1)[-1]
            header = "000"
            #print self.buffer
            while "$M>" not in header:
                #print "waiting header"
                if time.time() > start + 0.5:
                    print "timeout"
                    return None
                new = ""
                try:
                    new = self.ser.read(1)
                except :
                    print "timeout!"
                    return None
                header += new
                if len(header) > 3:
                    header = header[1:]
            #print "got header"
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
        receivedChecksum = ""
        while receivedChecksum == "":
            try:
                receivedChecksum = ord(self.ser.read())
            except:
                pass
        if command != expectedCommand:
            print("commands dont match!", command, expectedCommand, len(self.buffer))
            if receivedChecksum == checksum:  # was not supposed to arrive now, but data is data!
                #self.try_handle_response(command,data)
                #print "gotcha"
                #self.flush_input()
                pass
            return None
        if checksum == receivedChecksum:
            return data
        else:
            print ('lost packet!')
            return None

    def MSPquery(self, command):
        o = bytearray('$M<')
        c = 0
        o += chr(0)
        c ^= o[3]  #no payload
        o += chr(command)
        c ^= o[4]
        o += chr(c)
        answer = None
        while not answer:
            self.ser.write(o)
            answer = self.receiveAnswer(command)
        return answer

    def MSPquery16d(self, command, data=None):
        size = len(data) * 2
        o = bytearray('$M<')
        c = 0
        o += chr(size)
        c ^= o[3]  #no payload
        o += chr(command)
        c ^= o[4]
        for value in data:
            value = int(value)
            high = value >> 8  # The value of x shifted 8 bits to the right, creating coarse.
            low = value % 256
            o += chr(low)
            c ^= o[-1]
            o += chr(high)
            c ^= o[-1]
        o += chr(c)
        answer = None
        # print [int(i) for i in o]
        while answer is None:
            #print "waiting...11
            self.ser.write(o)
            answer = self.receiveAnswer(command)
            time.sleep(0.010)
        #        print "worked!"
        return answer


    def decode32(self, data):
        #print data
        result = (data[0] & 0xff) + ((data[1] & 0xff) << 8) + ((data[2] & 0xff) << 16) + ((data[3] & 0xff) << 24)
        is_negative = data[3] >= 128
        if is_negative:
            result -= 2 ** 32
        return result

    def decode16(self, data):
        #print data
        result = (data[0] & 0xff) + ((data[1] & 0xff) << 8)
        is_negative = data[1] >= 128
        if is_negative:
            result -= 2 ** 16
        return result


    def read_gps(self):
        print "requesting gps"
        answer = self.MSPquery(MSP_RAW_GPS)
        if answer:
            lat_list = answer[2:6]
            long_list = answer[6:10]
            latitude = self.decode32(lat_list) / 10000000.0
            longitude = self.decode32(long_list) / 10000000.0
            #print longitude,latitude
            return longitude, latitude
        return 0, 0

    def read_attitude(self, _nothing=None):
        #print "requesting attitude"
        answer = self.MSPquery(MSP_ATTITUDE)
        if answer:
            # print answer
            roll = self.decode16(answer[0:2]) / 10.0
            pitch = self.decode16(answer[2:4]) / 10.0
            mag = self.decode16(answer[4:6])
            self.attitude = (roll, pitch, mag)
            return roll, pitch, mag
        return 0, 0, 0

    def get_pid_names(self):
        if self.pidnames:
            return self.pidnames
        else:
            self.pidnames = "".join([chr(i) for i in self.MSPquery(MSP_PIDNAMES)]).split(";")[:-1]
        return self.pidnames

    def get_box_names(self):
        if self.boxnames:
            return self.boxnames
        else:
            self.boxnames = "".join([chr(i) for i in self.MSPquery(MSP_BOXNAMES)]).split(";")[:-1]
        return self.boxnames

    def chunks(self, l, n):
        if n < 1:
            n = 1
        return [l[i:i + n] for i in range(0, len(l), n)]

    def read_pid(self, params=None):
        pids = self.chunks(self.MSPquery(MSP_PID),3)
        names = self.get_pid_names()
        pid_list = []
        for i, name in enumerate(names):
            pid_list.append([name, pids[i]])
        self.pid_list = zip(names, pids)
        self.sender.queue(MSP_PID, self.pid_list)
        return self.pid_list

    def to_list(self, x):
        if x == None:
            return ()
        if type(x) != tuple:
            return x
        a, b = x
        return (self.to_list(a),) + self.to_list(b)

    def queue_pid_write(self, data):
        all = []
        for name,values in data:
            all.extend(values)
        print all
        self.MSPquery8d(MSP_SET_PID,all)

    def encode16(self,list):
        return list[0] + list[1] *256

    def MSPquery8d(self, command, data=None):
        size = len(data)
        o = bytearray('$M<')
        c = 0
        o += chr(size)
        c ^= o[3]  #no payload
        o += chr(command)
        c ^= o[4]
        for value in data:
            o += chr(value)
            c ^= o[-1]
        o += chr(c)
        answer = None
        while answer is None:
            self.ser.write(o)
            answer = self.receiveAnswer(command)
            time.sleep(0.10)
        return answer

    def get_status(self,extra=None):
        data = self.MSPquery(MSP_STATUS)
        micros = self.encode16(data[:2])
        status_flags = []
        status = ('angle', 'Horizon', 'baro', 'mag', 'headfree', 'headadj')
        flags = data[4] + data[5] * 256+ data[6] * 256* 256+ data[7] * 256 * 256 *256
        for i, flag in enumerate(status):
            if (flags >> i) % 2:
                status_flags.append(flag)
        #print data, micros, status_flags, f# lags, data[4], data[5],data[6], data[7]

    def write_eeprom(self, data = None):
        self.MSPquery(MSP_EEPROM_WRITE)

    def queue_eeprom(self, data = None):
        self.requested.append([self.write_eeprom,None])