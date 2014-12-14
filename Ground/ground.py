from view.overlay import Overlay
from view.videolink import Video
from gi.repository import Gtk
from telemetry_ground import Sender, Receiver
import time
import sys
from controls import Controls

class GroundStation():

    def __init__(self, ip):
        self.sender = Sender(ip)
        self.receiver = Receiver()           # thread that sends data
        self.sender.start()
        self.receiver.start()                # thread that receives data
        self.overlay = Overlay(self.receiver, self.sender)# overlay thread
        self.video = Video()                 # video thread
        self.controls = Controls(self.video) # controls thread
        self.controls.start()
        self.overlay.set_controls(self.controls)
        self.video.run()
        self.video.connect('configure_event', self.on_configure_event) # move master -> move dog
        self.video.connect('destroy', lambda w: Gtk.main_quit())  # close master -> end program

    def on_configure_event(self, *args):
        x, y = self.video.get_position()
        sx, sy = self.video.get_size()
        tx = self.video.get_style().xthickness
        self.overlay.move(x+tx, y+30)
        self.overlay.resize(sx, sy)


