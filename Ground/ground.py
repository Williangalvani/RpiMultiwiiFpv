from view.overlay import Overlay
from view.videolink import Video
from gi.repository import Gtk
from telemetry_ground import Sender, Receiver
import time
import sys

class GroundStation():

    def __init__(self, ip):
        self.sender = Sender(ip)
        self.receiver = Receiver()
        self.sender.start()
        self.receiver.start()
        self.overlay = Overlay(self.receiver)
        self.video = Video()
        self.video.run()
        self.video.connect('configure_event', self.on_configure_event) # move master -> move dog
        self.video.connect('destroy', lambda w: Gtk.main_quit()) # close master -> end program

    def on_configure_event(self, *args):
        x, y = self.video.get_position()
        sx, sy = self.video.get_size()
        tx = self.video.get_style().xthickness
        self.overlay.move(x+tx, y+30)
        self.overlay.resize(sx, sy)


if __name__ == "__main__":
    if len(sys.argv)<2:
        print "You must pass rpi IP as parameter"
        exit(0)
    GroundStation(sys.argv[1])
    Gtk.main()
    while True:
        time.sleep(1)
