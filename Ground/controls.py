__author__ = 'will'

import threading
import time

up_arrow = 111
down_arrow = 116
left = 113
right = 114
a = 38
s = 39
d = 40
w = 25

keymap = {'save': 41}

class Controls(threading.Thread):
    def __init__(self, overlay):
        threading.Thread.__init__(self)
        self.overlay = overlay
        self.overlay.set_controls(self)
        self.keys = {}
        self.channels = [1500 for i in range(8)]
        self.rchannels = [0 for i in range(4)]
        self.throttle = (w, s)
        self.pitch = (up_arrow, down_arrow)
        self.yaw = (a, d)
        self.roll = (left, right)
        self.channel_order = [self.roll,
                              self.pitch,
                              self.throttle,
                              self.yaw]
        self.channel_map = {'roll':     0,
                            'pitch':    1,
                            'yaw':      2,
                            'throttle': 3}

    def callback_press(self, widget, event):
        self.keys[event.get_keycode()[1]] = True

    def callback_release(self, widget, event):
        self.keys[event.get_keycode()[1]] = False
        #print self.keys

    def run(self):
        while True:
            # print self.channels
            time.sleep(0.1)
            for i, keys in enumerate(self.channel_order):
                down, up = keys
                mod = 0
                if self.getkey(down):
                    mod = + 100
                if self.getkey(up):
                    mod = - 100

                self.rchannels[i] += mod
                self.rchannels[i] *= 0.8
                self.channels[i] = self.rchannels[i]+1500

    def getkey(self, key):
        try:
            if isinstance(key,basestring):
                return self.keys[keymap[key]]
            return self.keys[key]
        except:
            return False

    def get_channel(self, n):
        if isinstance(n,basestring):
            return self.channels[self.channel_map[n]]
        return self.channels[n]
