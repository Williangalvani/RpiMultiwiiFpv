from protocol.messages import *

__author__ = 'will'


#!/usr/bin/env python

import cairo
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from math import sin, cos, radians, pi
import time


class Overlay(Gtk.Window):
    lens_x_angle = 53
    lens_y_angle = 22
    height = 0
    width = 0
    screen_mid_x = 0
    screen_mid_y = 0
    compass_x_off = 100
    compass_y_off = 200
    controls = None
    menu_on = False
    menu_selected = 1
    menu_x = 100
    menu_y = 200
    changed_menu = False
    changed_option = False
    boxes = {}

    rc_x = 50
    rc_y = 300
    # menu cursor pos
    ypos = 0
    xpos = 0
    pids = None

    def __init__(self, receiver, sender):
        super(Overlay, self).__init__(Gtk.WindowType(1))
        self.receiver = receiver
        self.sender = sender
        self.set_default_size(1366, 768)

        # overlay transparency
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual and self.screen.is_composited():
            self.set_visual(self.visual)

        self.set_position(Gtk.WindowPosition.CENTER)

        self.label = Gtk.Label()
        self.set_opacity(0.8)
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

    def set_controls(self, controls):
        self.controls = controls

    def draw(self, widget, cr):
        """Set transparent background and Draws HUD on top"""
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        if not self.controls.joystick_present:
            print "not present!"
            cr.select_font_face("Lucida Typewriter", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(20)
            cr.set_source_rgba(255,255,255,255)
            cr.move_to(self.screen_mid_x- 200,self.screen_mid_y)
            cr.show_text("Joystick disconnected!")
            cr.stroke()
        if not self.menu_on:
            self.draw_horizon(cr)
            self.draw_rssi(cr)
            self.draw_compass(cr)
            self.draw_status(cr)
            self.draw_altitude(cr)
            self.draw_rc(cr)
        else:
            self.draw_menu(cr)

    def draw_status(self, cr):
        _x = self.width - self.compass_x_off
        _y = self.compass_y_off + 200
        if 'status' in self.receiver.data.keys():
            for i, flag in enumerate(self.receiver.data['status']):
                cr.move_to(_x, _y + 30 * i)
                cr.show_text(flag)
        cr.stroke()

    def draw_altitude(self, cr):
        _x = self.width - 150
        _y = 80
        try:
            altitude, vario = self.receiver.get('attitude')[3:5]
            cr.move_to(_x, _y)
            cr.show_text("Alt: {0}M".format(altitude))
            cr.move_to(_x, _y + 20)
            cr.show_text("Var: {0}M/s".format(vario))
            cr.stroke()
        except:
            pass

    def draw_rssi(self, cr):
        cr.move_to(self.width - 150, 50)
        cr.show_text("Wi-FI:{0}%".format(self.receiver.get('RSSI')))
        cr.stroke()

    def draw_compass(self, cr):
        # cr.move_to(self.compass_x, self.compass_y)
        try:
            yaw = -radians(self.receiver.get('attitude')[2])
        except:
            return

        compass_x = self.width - self.compass_x_off
        compass_y = self.compass_y_off

        yoff = sin(yaw) * 50
        xoff = cos(yaw) * 50
        cr.set_line_width(2)
        cr.arc(compass_x, compass_y, 50, 0, 2 * pi)
        cr.move_to(compass_x,
                   compass_y)
        cr.line_to(compass_x + xoff,
                   compass_y + yoff)

        cr.move_to(compass_x + xoff * 1.4 - 10,
                   compass_y + yoff * 1.3 + 10)
        cr.show_text("N")
        cr.stroke()

    def draw_horizon(self, cr):
        """Draws horizon lines on screen """
        self.width, self.height = self.get_size()
        self.screen_mid_x = self.width / 2
        self.screen_mid_y = self.height / 2

        try:
            roll = radians(self.receiver.data['attitude'][0])
            pitch = self.receiver.data['attitude'][1]
        except:
            roll = 0
            pitch = 0

        def line_from_to(cr, x1, y1, x2, y2):
            cr.set_source_rgba(255, 255, 255, 255)
            cr.set_line_width(2)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.stroke()

        horizon_y = self.screen_mid_y - self.height * pitch / self.lens_y_angle
        length = 400.0
        height = sin(roll) * length
        width = cos(roll) * length
        cr.set_source_rgba(255, 255, 255, 255)
        cr.set_line_width(2)
        line_from_to(cr,
                     self.screen_mid_x - width / 2, horizon_y + height / 2,
                     self.screen_mid_x + width / 2, horizon_y - height / 2)

        cr.set_dash([10])
        cr.select_font_face("Lucida Typewriter", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(20)

        for i in range(-10, 10):
            y = horizon_y + 10.0 / self.lens_y_angle * i * self.height
            if 0 < y < self.height:
                points = [self.screen_mid_x - width / 2, y + height / 2,
                          self.screen_mid_x + width / 2, y - height / 2]
                line_from_to(cr, *points)

                cr.move_to(points[0] - 40, points[1])
                cr.show_text("{0}".format(-i * 10))
                cr.move_to(points[2], points[3])
                cr.show_text("{0}".format(-i * 10))
                cr.stroke()
        cr.set_dash([])
        self.draw_cross(cr)
        cr.stroke()

    def draw_cross(self, cr):
        """"Draws center cross on HUD"""
        cr.set_source_rgba(255, 255, 255, 255)
        cr.set_line_width(1)
        cr.move_to(self.screen_mid_x - 50, self.screen_mid_y)
        cr.line_to(self.screen_mid_x + 50, self.screen_mid_y)
        cr.stroke()

    def draw_rc(self, cr):
        """"Draws center cross on HUD"""
        cr.set_source_rgba(255, 255, 255, 255)
        cr.set_line_width(1)
        length = 100
        cr.rectangle(self.rc_x, self.rc_y, length, length)
        mid = self.rc_x + length / 2, self.rc_y + length / 2
        xoff = (self.controls.get_channel('yaw') - 1500) / 500.0 * 50
        yoff = (self.controls.get_channel('throttle') - 1500) / 500.0 * - 50
        cr.move_to(mid[0], mid[1])
        cr.line_to(mid[0] + xoff, mid[1] + yoff)
        cr.stroke()

        cr.rectangle(self.rc_x + length, self.rc_y, length, length)
        mid = self.rc_x + length + length / 2, self.rc_y + length / 2
        xoff = (self.controls.get_channel('roll') - 1500) / 500.0 * 50
        yoff = (self.controls.get_channel('pitch') - 1500) / 500.0 * - 50
        cr.move_to(mid[0], mid[1])
        cr.line_to(mid[0] + xoff, mid[1] + yoff)
        cr.stroke()


    def close(self, widget, event):
        """Finish Programm on double-click"""
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            Gtk.main_quit()

    def get_text(self):
        """ loads text string to show on top of the screen"""
        if 'attitude' in self.receiver.data:
            return """<span font="Arial Black 20" foreground="white"> Attitude:{0}</span>""".format(
                self.receiver.data['attitude'])
        else:
            return '---'

    def update_text(self):
        """Update text"""
        #
        # text = self.get_text()
        # if text is not None:
        # self.label.set_markup(text)
        pass

    def update_screen(self):
        if self.controls.getButton('menu'):
            self.menu_on = not self.menu_on
            time.sleep(0.2)
            if self.menu_on:
                self.sender.queue_message(MSP_PID)

    def draw_menu(self, cr):
        cr.set_source_rgba(255, 255, 255, 255)
        cr.select_font_face("Lucida Typewriter", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)

        self.sender.queue_message(MSP_PID)
        cr.set_font_size(20)
        max_x_pos = 0
        max_y_pos = 0
        if self.menu_selected == 1:
            max_x_pos = 3
            max_y_pos = 10
        elif self.menu_selected == 2:
            max_x_pos = 12
            max_y_pos = 10

        if self.controls.getButton('changemenu') and not self.changed_menu:
            self.menu_selected = (self.menu_selected + 1) % 3
            self.changed_menu = True
        if not self.controls.getButton('changemenu'):
            self.changed_menu = False

        # ################################################
        self.pitch_trigger = False
        pitch = self.controls.get_channel('pitch')
        # print "pitch: ", pitch
        if pitch > 1800 and not self.pitch_trigger:
            self.ypos -= 1
            self.ypos %= max_y_pos
            self.pitch_trigger = True

        elif pitch < 1200 and not self.pitch_trigger:
            self.ypos += 1
            self.ypos %=  max_y_pos
            self.pitch_trigger = True
        else:
            self.pitch_trigger = None

        ################################################
        self.roll_trigger = False
        roll = self.controls.get_channel('roll')
        # print "roll:",roll
        if roll > 1800 and not self.roll_trigger:
            self.xpos += 1
            self.xpos %= max_x_pos
            self.roll_trigger = True

        elif roll < 1200 and not self.roll_trigger:
            self.xpos -= 1
            self.xpos %= max_x_pos
            self.roll_trigger = True
        else:
            self.roll_trigger = None

        if self.menu_selected == 1:

            ################################################
            self.throttle_trigger = False
            throttle = self.controls.get_channel('throttle')
            #print "throttle:" , throttle
            if throttle > 1800 and not self.throttle_trigger:
                value = int(self.pids[self.ypos][1][self.xpos]) + 1
                self.pids[self.ypos][1][self.xpos] = value
                self.throttle_trigger = True

            elif throttle < 1200 and not self.throttle_trigger:
                value = int(self.pids[self.ypos][1][self.xpos]) - 1
                self.pids[self.ypos][1][self.xpos] = value
                self.throttle_trigger = True
            else:
                self.throttle_trigger = None
            ###############################################

            if self.controls.getButton('save'):
                self.sender.queue_message(MSP_SET_PID, self.pids)

            if self.controls.getButton('write'):
                self.sender.queue_message(MSP_EEPROM_WRITE)
            self.sender.queue_message(MSP_PID, None)
            cr.set_font_size(20)

            time.sleep(0.1)
            try:
                if not self.pids or self.controls.getButton('reload'):
                    self.pids = self.receiver.data['pid']
            except Exception, e:
                print Exception, e

            for line, pid in enumerate(self.pids):
                cr.move_to(self.menu_x, self.menu_y + 30 * line)
                name, values = pid
                string = name
                cr.show_text(string)
                for i, letter in enumerate(['P', 'I', 'D']):
                    selected = line == self.ypos and i == self.xpos
                    selected_str = "->" if selected else ""
                    cr.move_to(self.menu_x + 150 + 100 * i, self.menu_y + 30 * line)
                    cr.show_text('{0}{1}: {2}'.format(selected_str, letter, values[i]))
                cr.move_to(100, 100)
                cr.show_text("Press 'f' or 1 to send new pid, 'g' or 2 to write to eeprom, 'h' or 3 to reload")
                cr.stroke()

        elif self.menu_selected == 2:
            if 'box' in self.receiver.data:
                if not self.boxes:
                    self.boxes = self.receiver.data['box']
                for i in range(4):
                    cr.move_to(self.menu_x + 200 + 150 * i, self.menu_y - 70)
                    cr.show_text("AUX" + str(i+1))
                    for j, text in enumerate(["lo", "mid", "hi"]):
                        cr.move_to(self.menu_x + 200 + 150 * i + 50 * j, self.menu_y - 25)
                        cr.show_text(text)
                for i, line in enumerate(self.boxes.keys()):
                    cr.move_to(self.menu_x, self.menu_y + 30 * i)
                    cr.show_text(line)
                    for j in range(12):
                        selected = "->" if self.xpos == j and self.ypos == i else ""
                        cr.move_to(self.menu_x + 200 + 50*j, self.menu_y + 30 * i)
                        cr.show_text(selected + ("X" if self.boxes[line][j] else "-"))

                cr.move_to(self.menu_x,self.menu_y-100)
                cr.show_text("Press 1 to send new config, 2 to change, 3 to write")

                cr.stroke()

                if self.controls.getButton('changebox') and not self.changed_option:
                    self.changed_option = True
                    self.boxes[self.boxes.keys()[self.ypos]][self.xpos] = not self.boxes[self.boxes.keys()[self.ypos]][self.xpos]
                if not self.controls.getButton('changebox'):
                    self.changed_option = False

                if self.controls.getButton('box_write'):
                    self.sender.queue_message(MSP_EEPROM_WRITE)
                if self.controls.getButton('save'):
                    self.sender.queue_message(MSP_SET_BOX, self.boxes)


    def update_overlay(self):
        """Callback function for timer"""
        self.update_text()
        self.update_screen()
        self.queue_draw()
        GObject.timeout_add(50, self.update_overlay)

