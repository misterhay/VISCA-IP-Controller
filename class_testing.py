#! /usr/bin/python

from time import sleep
import camera as cm



c = cm.Camera('192.168.0.100', 52381)
c.multiply(3,4)
print(c.sequence_number)
c.disconnect()
#print(cm.camera_on)

