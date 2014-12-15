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

keymap = {'save': 41}

class Controls(threading.Thread):
    def __init__(self, overlay):
        threading.Thread.__init__(self)
        self.overlay = overlay
        self.overlay.set_controls(self)
        self.keys = {}
        self.channels = [1000 for i in range(8)]
        self.rchannels = [0 for i in range(8)]
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


        self.buttons = [0 for i in range( 10)]
        self.joystick_present = False

        try:
            pygame.init()
            pygame.joystick.init()

            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.n_axes = self.joystick.get_numaxes()
            self.n_buttons= self.joystick.get_numbuttons()
            self.joystick_present = True
        except Exception, e:
            print e

    def callback_press(self, widget, event):
        self.keys[event.get_keycode()[1]] = True

    def callback_release(self, widget, event):
        self.keys[event.get_keycode()[1]] = False
        #print self.keys

    def run(self):
        while True:
            # print self.channels
            time.sleep(0.1)
            if not self.joystick_present:
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
            else:
                    axis = [self.joystick.get_axis(axis1)*100 for axis1 in range(self.n_axes)]
                    self.rchannels[self.channel_map['throttle']] = 1500-5*axis[1]
                    self.rchannels[self.channel_map['yaw']] = 1500+5*axis[0]
                    self.rchannels[self.channel_map['pitch']] = 1500-5*axis[3]
                    self.rchannels[self.channel_map['roll']] = 1500+5*axis[2]
                    self.buttons = [self.joystick.get_button(but)*100 for but in range(self.n_buttons)]
                    print self.buttons

                    if self.buttons[5]:
                        self.rchannels[4]= 1950
                    elif self.buttons[7]:
                        self.rchannels[4] = 1050

                    for event in pygame.event.get():
                          pass
                    print self.rchannels

    time.sleep(0.1)



    def getkey(self, key):
        try:
            if isinstance(key,basestring):
                return self.keys[keymap[key]]
            return self.keys[key]
        except:
            return False

    def getButton(self,n):
        return self.buttons[n-1]

    def get_channel(self, n):
        if isinstance(n,basestring):
            return self.rchannels[self.channel_map[n]]
        return self.rchannels[n]
