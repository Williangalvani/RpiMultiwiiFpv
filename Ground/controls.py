__author__ = 'will'

import threading
import time
import pygame


class Controls(threading.Thread):
    def __init__(self, overlay):
        threading.Thread.__init__(self)

        self.expo_rate = 0
        self.channel_map = {'roll': 0,      ## the desired channels order.
                            'pitch': 1,
                            'yaw': 2,
                            'throttle': 3}

        self.channels_center = {'roll': 1500,   ## the center of each channel
                                'pitch': 1500,
                                'yaw': 1500,
                                'throttle': 1500}

        self.buttons_map = {'menu': 10,
                            'save': 1,
                            'write': 2,
                            'reload': 3,
                            'arm': 6,
                            'disarm': 8,
                            'changemenu':9,
                            'changebox': 2,
                            'box_write':3,
                            'baro_on':5,
                            'baro_off':7}

        self.directionals = {'up': False,
                             'down': False,
                             'left': False,
                             'right': False}

        self.channels = [1000 for i in range(8)]  # [1000; 2000]
        self.raw_channels = [0 for i in range(8)]  # [-500;  500]
        self.buttons = [0 for i in range(10)]  # joystick buttons
        self.joystick_present = False
        pygame.init()
        pygame.joystick.init()


    def connect(self):
        print "connecting"
        pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count():
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.n_axes = self.joystick.get_numaxes()
            self.n_buttons = self.joystick.get_numbuttons()
            self.joystick_present = True
            print "connected"
        else:
            time.sleep(1)

    def run(self):
        map = self.channel_map
        centers = self.channels_center
        expo = self.expo

        while True:
            if not self.joystick_present:
                self.connect()
            else:
                time.sleep(0.05)

                # # necessary for pygame to read the joystick
                for event in pygame.event.get():
                    pass
                print self.raw_channels

                ## process axis
                axis = [self.joystick.get_axis(axis1) * 100 for axis1 in range(self.n_axes)]

                self.raw_channels[map['throttle']] = expo(centers['throttle'], -axis[1])
                self.raw_channels[map['yaw']] =      expo(centers['yaw'], axis[0])
                self.raw_channels[map['pitch']] =    expo(centers['pitch'], -axis[3])
                self.raw_channels[map['roll']] =     expo(centers['roll'], axis[2])

                ## process buttons
                self.buttons = [self.joystick.get_button(but) * 100 for but in range(self.n_buttons)]
                print self.buttons

                ### process directionals (hat)
                directionals = self.joystick.get_hat(0)
                self.directionals['up'] = directionals[1] == 1
                self.directionals['down'] = directionals[1] == -1
                self.directionals['left'] = directionals[0] == -1
                self.directionals['right'] = directionals[0] == 1

                ###### evaluate effects
                if self.getButton('arm'):
                    self.raw_channels[4] = 1950
                elif self.getButton('disarm'):  # disarm#
                    self.raw_channels[4] = 1050

                if self.getButton('baro_on'):
                    self.raw_channels[5] = 1950
                elif self.getButton('baro_off'):  # disarm#
                    self.raw_channels[5] = 1050

                ##Trimming
                if self.directionals['up']:
                    self.channels_center['throttle'] += 1
                if self.directionals['down']:
                    self.channels_center['throttle'] -= 1
                if self.directionals['left']:
                    self.channels_center['yaw'] += 1
                if self.directionals['right']:
                    self.channels_center['yaw'] += 1

    def expo(self, center, value):
        x = abs(value) / 100.0
        a = self.expo_rate
        expo = a * x * x + (1 - a) * x
        if value >= 0:
            return center + expo * (2000 - center )
        else:
            return center - expo* (center - 1000 )

    def getButton(self, n):
        if isinstance(n, basestring):
            return self.getButton(self.buttons_map[n])
        return self.buttons[n - 1]

    def get_channel(self, n):
        """returns nth channel, or mapped from string"""
        if isinstance(n, basestring):
            return self.raw_channels[self.channel_map[n]]
        return self.raw_channels[n]
