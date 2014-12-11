__author__ = 'will'
from Ground.ground import GroundStation
from gi.repository import Gtk
import time
import sys


if __name__ == "__main__":
    if len(sys.argv)<2:
        print "You must pass rpi IP as parameter"
        exit(0)
    GroundStation(sys.argv[1])
    Gtk.main()
    while True:
        time.sleep(1)
c