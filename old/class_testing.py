#! /usr/bin/python

# https://github.com/Sciguymjm/python-visca/blob/master/visca/camera.py
# https://github.com/Electronics/ViscaOverIP/blob/master/PTZcamera.py
# https://github.com/Electronics/ViscaOverIP/blob/master/commands.py
### https://brightsign.zendesk.com/hc/en-us/community/posts/360020803753-Multicast-Streaming-to-BrightSign-s-via-OBS

import camera as cm

c = cm.Camera('192.168.0.100', 52381)
#c.multiply(3,4)
print(c.sequence_number)
c.disconnect()
#print(cm.camera_on)

