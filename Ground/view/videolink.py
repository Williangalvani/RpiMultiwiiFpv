__author__ = 'will'
#!/usr/bin/python3
#   gst-launch -v udpsrc port=4001 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264'
#   ! \ rtph264depay ! ffdec_h264 ! xvimagesink sync=false

import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GdkPixbuf
from gi.repository import Gtk
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo
import cairo

from overlay import Overlay

GObject.threads_init()
Gst.init(None)


class Video (Gtk.Window):
    def __init__(self):
        super(Video, self).__init__()
        self.connect('destroy', self.quit)
        self.set_default_size(1366, 768)

        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        self.set_decorated(True)
        self.image = Gtk.Image()

        self.videowidget = Gtk.DrawingArea()
        self.add(self.videowidget)
        self.videowidget.set_size_request(*self.get_size())
        self.videowidget.show()

        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        # Create GStreamer elements
        self.src = Gst.ElementFactory.make('udpsrc', None)
        self.src.set_property("port", 5004)
        caps = Gst.caps_from_string('application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264')
        self.src.set_property("caps", caps)
        self.depay = Gst.ElementFactory.make("rtph264depay", None)
        self.src.connect("pad-added", self.on_pad_added)
        self.decode = Gst.ElementFactory.make("avdec_h264", None)
        self.convert = Gst.ElementFactory.make("videoconvert",None)
        self.sink = Gst.ElementFactory.make('xvimagesink', None)
        self.sink.set_property('sync', False)

        # Add elements to the pipeline
        self.pipeline.add(self.src)
        self.pipeline.add(self.depay)
        self.pipeline.add(self.decode)
        self.pipeline.add(self.convert)
        self.pipeline.add(self.sink)

        self.src.link(self.depay)
        self.depay.link(self.decode)
        self.decode.link(self.convert)
        self.convert.link(self.sink)


    def on_pad_added(self, element, pad):
        if "video" in name:
            sink_pad = self.depay.get_request_pad("sink")
            pad.link(sink_pad)

    def run(self):
        self.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid = self.videowidget.get_property('window').get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        print "syncing"
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())



weatherurl = "http://31.44.177.1/weather"
texturl = "http://31.44.177.1/gettext"

overlay = Overlay()


webcam = Video()

webcam.run()
Gtk.main()