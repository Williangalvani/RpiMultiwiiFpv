#RpiMultiWiiFpv

This is an attempt at a wi-fi only fpv setup using MultiWii, Raspberry Pi B, 
and a laptop with joystick.

[![Youtube playlist](http://galvanicloop.com/media/other/rpi.png)](https://www.youtube.com/playlist?list=PLwy4WgVQICvmDAN-mdecU3r97ztXYPF8n)


##Requirements:##
###On the Rpi:
- Pyserial
- gstreamer-1.0
- rpi camera enabled

###On the ground:
- gstreamer-1.0

##Usage:##
###On the Pi:###
*`cd fpv/`*

*`python air.py`*

###On the Pc:###
*`cd fpv/`*

*`python ground.py [raspberry IP])`*
