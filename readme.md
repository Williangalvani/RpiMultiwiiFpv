# RpiMultiWiiFpv

This is an attempt at a wi-fi only fpv setup using MultiWii, Raspberry Pi B,
and a laptop with joystick. It streams the video via UDP, and both reads telemetry and sends joystick inputs via another UDP socket.

The initial tests can be seen here (link to youtube playlist of tests):
[![Youtube playlist](http://galvanicloop.com/media/other/rpi.png)](https://www.youtube.com/playlist?list=PLwy4WgVQICvmDAN-mdecU3r97ztXYPF8n)

The video delay was around 200ms, joystick input probably less, However a joystick is a lousy way to control a drone, since it's not nearly as sensitive as a proper controller and have a large central 
deadzone, with lead me to [build a proper openLRS radio](http://galvanicloop.com/blog/post/10/frankstxein-opentx-openlrsng-telemetry)


## Requirements:
### On the Rpi:
- Pyserial
- gstreamer-1.0
- rpi camera enabled

### On the ground:
- gstreamer-1.0

## Usage:
### On the Pi:
*`cd fpv/`*

*`python air.py`*

### On the Pc:
*`cd fpv/`*

*`python ground.py <raspberry IP>`*
