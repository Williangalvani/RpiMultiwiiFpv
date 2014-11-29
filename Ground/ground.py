from view.overlay import Overlay
from view.videolink import Video
from gi.repository import Gtk
from telemetry_ground import Sender, Receiver

class GroundStation():
    def __init__(self):
        self.overlay = Overlay()
        self.video = Video()
        self.video.run()
        self.video.connect('configure_event', self.on_configure_event) # move master -> move dog
        self.video.connect('destroy', lambda w: Gtk.main_quit()) # close master -> end program

        sender = Sender()
        receiver = Receiver()
        sender.start()
        receiver.start()
        self.overlay.setReceiver(receiver)
        Gtk.main()

    def on_configure_event(self, *args):
        print "Window 1 moved!"
        x, y   = self.video.get_position()
        sx, sy = self.video.get_size()
        tx = self.video.get_style().xthickness
        self.overlay.move(x+tx, y+30)


GroundStation()