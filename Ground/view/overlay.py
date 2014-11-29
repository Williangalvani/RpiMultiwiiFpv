__author__ = 'will'


#!/usr/bin/env python

import cairo
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository.GdkPixbuf import Pixbuf
import urllib2


class Overlay (Gtk.Window):
    def __init__(self):
        super(Overlay, self).__init__(Gtk.WindowType(1))
        print "created"
        self.set_position(Gtk.WindowPosition.CENTER)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        self.set_decorated(True)
        self.image = Gtk.Image()
        self.label = Gtk.Label()
        self.set_opacity(0.8)
        self.set_modal(True)
        self.set_keep_above(True)
        self.timer = 0
        self.receiver = None
        img_size = (0,0)

        try:
            pixbuf = Pixbuf.new_from_file("banner.png")
        except:
            pass
        else:
            self.image.set_from_pixbuf(pixbuf)
            img_size = (pixbuf.get_width(), pixbuf.get_height())
            self.move(10, self.screen.get_height()-img_size[1]-20)

        if self.visual != None and self.screen.is_composited():
            self.set_visual(self.visual)

        self.label.show()
        self.label.set_alignment(0, 0.0)

        box = Gtk.Box()
        ebox = Gtk.EventBox()
        align = Gtk.Alignment()
        align.set_valign(1)
        align.add(self.image)
        ebox.set_visible_window(False)
        ebox.add(align)
        box.pack_start(ebox, False, False, 0)

        box.pack_start(self.label, False, False, 0)

        self.add(box)

        self.set_app_paintable(True)
        self.connect("draw", self.draw)
        box.connect("button-press-event", self.close)
        self.show_all()
        GObject.timeout_add(100, self.timer_func)

    def draw(self, widget, cr):
        """Set transparent background"""
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    def setReceiver(self,receiver):
        self.receiver = receiver

    def close(self, widget, event):
        """Finish Programm on double-click"""
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            Gtk.main_quit()

    def get_image(self):
        """Download image and save it to file"""
        try:
            req = urllib2.Request(weatherurl)
            res = urllib2.urlopen(req)
            if (res.code==200):
                f = open("banner.png", "w")
                f.write(res.read())
                f.close
        except:
            return None

    def get_text(self):
        """Get text and return it"""
        if 'attitude' in self.receiver.data:
            return """<span font="Arial Black 20" foreground="white"> Attitude:{0}</span>""".format(self.receiver.data['attitude'])
        else:
            return '---'

    def update_image(self):
        """Update image"""
        self.get_image()
        try:
            pixbuf = Pixbuf.new_from_file("banner.png")
        except:
            pass
        else:
            img_size = (pixbuf.get_width(), pixbuf.get_height())
            # self.move(10, self.screen.get_height()-img_size[1]-20)
            self.image.set_from_file("banner.png")

    def update_text(self):
        """Update text"""
        text = self.get_text()

        if text is not None:
            self.label.set_markup(text)

    def timer_func(self):
        """Callback function for timer"""
        self.update_text()
        # self.update_image()
        GObject.timeout_add(100, self.timer_func)


weatherurl = "http://31.44.177.1/weather"
texturl = "http://31.44.177.1/gettext"
# app = Overlay()
# Gtk.main()
#

