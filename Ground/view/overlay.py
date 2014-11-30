__author__ = 'will'


#!/usr/bin/env python

import cairo
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository.GdkPixbuf import Pixbuf
import urllib2
from hud_renderer import HudRenderer

class Overlay (Gtk.Window):
    def __init__(self, receiver):
        super(Overlay, self).__init__(Gtk.WindowType(1))
        self.receiver = receiver

        #overlay transparency
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual != None and self.screen.is_composited():
            self.set_visual(self.visual)

        self.set_position(Gtk.WindowPosition.CENTER)
        # self.set_decorated(True)
        self.image = Gtk.Image()
        self.label = Gtk.Label()
        self.set_opacity(0.8)
        # self.set_modal(True)
        self.set_keep_above(True)
        self.textRenderer = HudRenderer(self.receiver)
        self.update_image()
        self.update_text()

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

        #more on the invisibility
        self.set_app_paintable(True)
        self.connect("draw", self.draw)
        box.connect("button-press-event", self.close)

        self.show_all()

        GObject.timeout_add(100, self.update_overlay)

    def draw(self, widget, cr):
        """Set transparent background"""
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.set_source_rgba(255, 255, 255, 255)
        cr.set_line_width(2)
        cr.move_to(0, 0)
        cr.line_to(100, 100)
        cr.stroke()

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
                f.close()
        except:
            return None

    def get_text(self):
        return self.textRenderer.get_screen()

    def update_image(self):
        """Update image"""
        self.get_image()
        self.image.set_from_file("banner.png")

    def update_text(self):
        """Update text"""
        text = self.get_text()
        if text is not None:
            self.label.set_markup(text)

    def update_overlay(self):
        """Callback function for timer"""
        self.update_text()
        # self.update_image()
        GObject.timeout_add(100, self.update_overlay)


weatherurl = "http://31.44.177.1/weather"
texturl = "http://31.44.177.1/gettext"


