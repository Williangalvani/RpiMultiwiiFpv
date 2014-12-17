from protocol.messages import *
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


def decode_32(data):
    result = (data[0] & 0xff) + ((data[1] & 0xff) << 8) + ((data[2] & 0xff) << 16) + ((data[3] & 0xff) << 24)
    is_negative = data[3] >= 128
    if is_negative:
        result -= 2 ** 32
    return result


def decode_16(data):
    result = (data[0] & 0xff) + ((data[1] & 0xff) << 8)
    is_negative = data[1] >= 128
    if is_negative:
        result -= 2 ** 16
    return result


def encode_16(lista):
    return lista[0] + lista[1] * 256


class TelemetryReader():
    def __init__(self):
        self.run = True
        self.thread = FuncThread(self.loop)
        self.thread.start()

        self.attitude = [0, 0, 0, 0, 0]
        self.buffer = ""
        self.ser = None
        self.sender = None
        self.requested = []  # special messages on request
        self.periodic = [(self.read_attitude, None),
                         (self.read_attitude, None),
                         (self.read_attitude, None),
                         (self.get_status, None)]  # regular messages, sent one each cycle
        self.periodic_len = len(self.periodic)
        self.msg_counter = 0
        self.pid_names = []
        self.pid_list = []
        self.status_flags = []
        self.connected = False
        self.last_time_baro = time.time()
        self.box_names = None
        self.last_time_joystick_received = 0

    def reset_rc(self):
        print "rc timeout!"
        self.queue_rc([1000 for i in range(8)])

    def loop(self):
        while self.run:
            try:
                # keeping hardcoded, since it's the rpi builting serial.
                self.ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1)
                self.ser.flushInput()
                self.connected = True
                print "connected to serial port", self.ser
            except Exception, e:
                print "could not connect, retrying in 3s\n", e
                time.sleep(3)
            if self.connected:
                try:
                    while self.run:
                        if time.time() - self.last_time_joystick_received > 1:
                            self.reset_rc()

                        if self.requested:
                            function, params = self.requested.pop(0)
                            function(params)
                        else:
                            function, params = self.periodic[self.msg_counter % self.periodic_len]
                            function(params)
                            self.msg_counter += 1
                except Exception, e:
                    print "Error on serial loop:", e
                    print traceback.format_exc()

    def stop(self):
        """sets flag to stop thread"""
        self.run = False

    def set_sender(self, sender):
        """sets it's udp socket sender"""
        self.sender = sender

#### queuing methods... i don't like the way it looks.
    def queue_rc(self, rc_list):
        self.last_time_joystick_received = time.time()
        self.requested.append((self.write_rc, rc_list))

    def queue_pid_request(self):
        self.requested.append((self.read_pid, []))

    def queue_pid_write(self, data):
        all_pids = []
        for name, values in data:
            all_pids.extend(values)
        self.requested.append((self.pid_write, all_pids))

    def queue_eeprom(self, data=None):
        request = (self.write_eeprom, None)
        print len(self.requested), self.requested
        if request not in self.requested:
            self.requested.append(request)

##############   Writing methods:  #################################
    def write_eeprom(self, data=None):
        print self.MSPquery(MSP_EEPROM_WRITE)

    def pid_write(self, data):
            self.MSPquery8d(MSP_SET_PID, data)

    def write_rc(self, rc_list):
        self.MSPquery16d(MSP_SET_RAW_RC, rc_list)

#############################3

    def read(self, n=1):
        """
        Tries to read one byte from serial, loops until it can, or 1 seconds times out
        """
        result = ""
        start = time.time()
        while len(result) != n:
            try:
                result = result + self.ser.read(1)
            except Exception, e:
                print "Exception while reading:", e
            if (time.time() - start) > 1:
                raise serial.SerialTimeoutException
        return result

    def receive_answer(self, expected_command):
        time.sleep(0.0001)
        command = None
        size = 0
        start = time.time()
        while command != expected_command:
            if time.time() > start + 0.5:
                print "timeout"
                return None
            if len(self.buffer) > 15:
                self.buffer = "$M>" + self.buffer.rsplit("$M>", 1)[-1]
            header = "000"
            while "$M>" not in header:
                if time.time() > start + 0.5:
                    print "timeout"
                    return None
                try:
                    new = self.ser.read(1)
                except Exception, e:
                    print "timeout!", e
                    return None
                header += new
                if len(header) > 3:
                    header = header[1:]
            size = ord(self.read())
            command = ord(self.read())
            if command != expected_command:
                print "wrong command! expected:", expected_command, " got:", command
        data = []
        for i in range(size):
            data.append(ord(self.ser.read()))
        checksum = 0
        checksum ^= size
        checksum ^= command
        for i in data:
            checksum ^= i
        received_checksum = ""
        while received_checksum == "":
            try:
                received_checksum = ord(self.ser.read())
            except:
                pass
        if command != expected_command:
            print("commands don't match!", command, expected_command, len(self.buffer))
            if received_checksum == checksum:  # was not supposed to arrive now, but data is data!
                pass
        if checksum == received_checksum:
            if not data:
                return True
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
            answer = self.receive_answer(command)
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
        while answer is None:
            self.ser.write(o)
            answer = self.receive_answer(command)
            time.sleep(0.010)
        return answer

    def read_gps(self):
        print "requesting gps"
        answer = self.MSPquery(MSP_RAW_GPS)
        if answer:
            lat_list = answer[2:6]
            long_list = answer[6:10]
            latitude = decode_32(lat_list) / 10000000.0
            longitude = decode_32(long_list) / 10000000.0
            return longitude, latitude
        return 0, 0

    def read_attitude(self, _nothing=None):
        answer = self.MSPquery(MSP_ATTITUDE)
        roll, pitch, mag, altitude, vario = self.attitude
        if answer:
            roll = decode_16(answer[0:2]) / 10.0
            pitch = decode_16(answer[2:4]) / 10.0
            mag = decode_16(answer[4:6])

        if (time.time() - self.last_time_baro) > 0.5:
            answer = self.MSPquery(MSP_ALTITUDE)
            if answer:
                altitude = decode_32(answer[:4]) / 100.0
                vario = decode_16(answer[4:6]) / 100.0
                self.last_time_baro = time.time()

        self.attitude = [roll, pitch, mag, altitude, vario]
        return self.attitude

    def get_pid_names(self):
        if self.pid_names:
            return self.pid_names
        else:
            self.pid_names = "".join([chr(i) for i in self.MSPquery(MSP_PIDNAMES)]).split(";")[:-1]
        return self.pid_names

    def get_box_names(self):
        if self.box_names:
            return self.box_names
        else:
            self.box_names = "".join([chr(i) for i in self.MSPquery(MSP_BOXNAMES)]).split(";")[:-1]
        return self.box_names

    def chunks(self, l, n):
        if n < 1:
            n = 1
        return [l[i:i + n] for i in range(0, len(l), n)]

    def read_pid(self, params=None):
        pids = self.chunks(self.MSPquery(MSP_PID), 3)
        names = self.get_pid_names()
        pid_list = []
        for i, name in enumerate(names):
            pid_list.append([name, pids[i]])
        self.pid_list = zip(names, pids)
        self.sender.queue(MSP_PID, self.pid_list)
        return self.pid_list

    def to_list(self, x):
        if x is None:
            return ()
        if type(x) != tuple:
            return x
        a, b = x
        return (self.to_list(a),) + self.to_list(b)

    def MSPquery8d(self, command, data=None):
        size = len(data)
        o = bytearray('$M<')
        c = 0
        o += chr(size)
        c ^= o[3]           # no payload
        o += chr(command)
        c ^= o[4]
        for value in data:
            o += chr(value)
            c ^= o[-1]
        o += chr(c)
        answer = None
        while answer is None:
            self.ser.write(o)
            answer = self.receive_answer(command)
            time.sleep(0.10)
        return answer

    def get_status(self, extra=None):
        """
        reads status data from Multiwii
        and tries to reassemble the data, poorly
        """
        data = self.MSPquery(MSP_STATUS)
        micros = encode_16(data[:2])
        status_flags = []
        status = ('Stable', '', '', '', '', '', '1', '2', '3', '3', '4', '5', '6', '7', '8', '9', 'Armed')
        flags = data[4] + data[5] * 256 + data[6] * 256 * 256 + data[7] * 256 * 256 * 256
        for i, flag in enumerate(status):
            if (flags >> i) % 2:
                if len(flag):
                    status_flags.append(flag)
        self.status_flags = status_flags
        return status_flags
