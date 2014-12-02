__author__ = 'will'


#!/usr/bin/env python

import cairo
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from math import sin,cos,radians

class Overlay (Gtk.Window):
    xangle = 53
    yangle = 22
    def __init__(self, receiver):
        super(Overlay, self).__init__(Gtk.WindowType(1))
        self.receiver = receiver

        self.set_default_size(1366, 768)
        #overlay transparency
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual != None and self.screen.is_composited():
            self.set_visual(self.visual)

        self.set_position(Gtk.WindowPosition.CENTER)

        self.label = Gtk.Label()
        self.set_opacity(0.8)
        # self.set_modal(True)
        self.set_keep_above(True)

        self.update_text()

        self.label.show()
        self.label.set_alignment(0, 0.0)

        box = Gtk.Box()
        ebox = Gtk.EventBox()
        align = Gtk.Alignment()
        align.set_valign(1)
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
        self.draw_horizon(cr)

    def draw_horizon(self,cr):
        self.width, self.height = self.get_size()
        self.midx = self.width/2
        self.midy = self.height/2

        try:
            roll= radians(self.receiver.data['attitude'][0])
            pitch= self.receiver.data['attitude'][1]
        except:
            roll=0
            pitch = 0

        def line_from_to(cr,x1,y1,x2,y2):
            cr.set_source_rgba(255, 255, 255, 255)
            cr.set_line_width(2)
            cr.move_to(x1,y1)
            cr.line_to(x2,y2)
            cr.stroke()

        #print roll
        horizon_y = self.midy - self.height * pitch/self.yangle
        length = 400.0
        height = sin(roll)*length
        width = cos(roll)*length
        #print height, horizon_y, self.height, pitch, self.yangle
        cr.set_source_rgba(255, 255, 255, 255)
        cr.set_line_width(2)
        line_from_to(cr,
                     self.midx - width/2, horizon_y + height/2,
                     self.midx + width/2, horizon_y - height/2)


        cr.set_dash([10])
        cr.select_font_face("Lucida Typewriter", cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(20)

        for i in range(-10,10):
            y = horizon_y + 10.0/self.yangle * i * self.height
            if 0 < y < self.height:
                points = [self.midx - width/2, y + height/2,
                             self.midx + width/2, y - height/2]
                line_from_to(cr, *points)

                cr.move_to(points[0]-40,points[1])
                cr.show_text("{0}".format(-i*10))
                cr.move_to(points[2],points[3])
                cr.show_text("{0}".format(-i*10))
                cr.stroke()
        cr.set_dash([])




        self.draw_cross(cr)

        cr.stroke()


    def draw_cross(self,cr):
        cr.set_source_rgba(255, 255, 255, 255)
        cr.set_line_width(1)
        cr.move_to(self.midx - 50, self.midy)
        cr.line_to(self.midx + 50, self.midy)
        cr.stroke()



    def close(self, widget, event):
        """Finish Programm on double-click"""
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            Gtk.main_quit()

    def get_text(self):
        if 'attitude' in self.receiver.data:
            return """<span font="Arial Black 20" foreground="white"> Attitude:{0}</span>""".format(self.receiver.data['attitude'])
        else:
            return '---'

    def update_text(self):
        """Update text"""
        text = self.get_text()
        if text is not None:
            self.label.set_markup(text)

    def update_overlay(self):
        """Callback function for timer"""
        self.update_text()
        self.queue_draw()
        # self.update_image()
        GObject.timeout_add(50, self.update_overlay)

