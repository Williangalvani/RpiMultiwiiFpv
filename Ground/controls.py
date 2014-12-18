__author__ = 'will'

import threading
import time
import pygame


up_arrow = 111
down_arrow = 116
left = 113
right = 114
a = 38
s = 39
d = 40
w = 25

keymap = {'save': 41,
          'eeprom': 42,
          'reload': 43}


class Controls(threading.Thread):

    def __init__(self, overlay):
        threading.Thread.__init__(self)
        self.channels = [1000 for i in range(8)]  # [1000; 2000]
        self.raw_channels = [0 for i in range(8)]  # [-500;  500]

        self.overlay = overlay
        self.overlay.set_controls(self)

        self.keys = {}  # each key on the keyboard is a key on this dict either true or false
        self.expo_rate = 0
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

        self.buttons = [0 for i in range(10)]  # joystick buttons
        self.joystick_present = False

        try:
            pygame.init()
            pygame.joystick.init()

            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.n_axes = self.joystick.get_numaxes()
            self.n_buttons = self.joystick.get_numbuttons()
            self.joystick_present = True
        except Exception, e:
            print e

    def callback_press(self, widget, event):
        self.keys[event.get_keycode()[1]] = True

    def callback_release(self, widget, event):
        self.keys[event.get_keycode()[1]] = False

    def run(self):
        while True:
            time.sleep(0.05)
            if not self.joystick_present:
                for i, keys in enumerate(self.channel_order):
                    decrease, increase = keys
                    mod = 0
                    if self.getkey(decrease):
                        mod = + 100
                    if self.getkey(increase):
                        mod = - 100

                    self.raw_channels[i] += mod
                    self.raw_channels[i] *= 0.8
                    self.channels[i] = self.raw_channels[i]+1500
            else:
                    ## necessary for pygame to read the joystick
                    for event in pygame.event.get():
                          pass
                    print self.raw_channels

                    axis = [self.joystick.get_axis(axis1)*100 for axis1 in range(self.n_axes)]

                    self.raw_channels[self.channel_map['throttle']] = 1500-500 * self.expo(axis[1])
                    self.raw_channels[self.channel_map['yaw']] = 1500+500 * self.expo(axis[0])
                    self.raw_channels[self.channel_map['pitch']] = 1500-500 * self.expo(axis[3])
                    self.raw_channels[self.channel_map['roll']] = 1500+500 * self.expo(axis[2])

                    self.buttons = [self.joystick.get_button(but)*100 for but in range(self.n_buttons)]
                    print self.buttons

                    if self.buttons[5]:   #arm
                        self.raw_channels[4] = 1950
                    elif self.buttons[7]:  # disarm#
                        self.raw_channels[4] = 1050

    def expo(self, value):
        x = abs(value) / 100.0
        a = self.expo_rate
        expo = a*x*x + (1-a) * x
        if value >= 0 :
            return expo
        else:
            return -expo

    def getkey(self, key):
        """ gets a key state either by numeric value or from mapped string"""
        try:
            if isinstance(key, basestring):
                return self.keys[keymap[key]]
            return self.keys[key]
        except:
            return False

    def getButton(self, n):
        return self.buttons[n-1]

    def get_channel(self, n):
        """returns nth channel, or mapped from string"""
        if isinstance(n, basestring):
            return self.raw_channels[self.channel_map[n]]
        return self.raw_channels[n]
