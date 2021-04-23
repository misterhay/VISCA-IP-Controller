# VISCA camera hex payloads

camera_on = '81 01 04 00 02 FF'
camera_off = '81 01 04 00 03 FF'

information_display_on = '81 01 7E 01 18 02 FF'
information_display_off = '81 01 7E 01 18 03 FF'

zoom_stop = '81 01 04 07 00 FF'
zoom_tele = '81 01 04 07 02 FF'
zoom_wide = '81 01 04 07 03 FF'
zoom_tele_variable = '81 01 04 07 2p FF' # p=0 (Low) to 7 (High)
zoom_wide_variable = '81 01 04 07 3p FF' # p=0 (Low) to 7 (High)
zoom_direct = '81 01 04 47 0p 0q 0r 0s FF' # pqrs = Zoom Position

memory_reset = '81 01 04 3F 00 0p FF'
memory_set = '81 01 04 3F 01 0p FF' # p = memory number (0 to F)
memory_recall = '81 01 04 3F 02 0p FF' # p: memory number (0 to F)

#Pan-tilt Drive
# VV: Pan speed setting 0x01 (low speed) to 0x18
# WW: Tilt speed setting 0x01 (low speed) to 0x17
# YYYY: Pan Position DE00 to 2200 (CENTER 0000)
# ZZZZ: Tilt Position FC00 to 1200 (CENTER 0000)

pan_up = '81 01 06 01 VV WW 03 01 FF'.replace('VV', str(18))
pan_down = '81 01 06 01 VV WW 03 02 FF'.replace('VV', str(18))
pan_left = '81 01 06 01 VV WW 01 03 FF'.replace('VV', str(18))
pan_right = '81 01 06 01 VV WW 02 03 FF'.replace('VV', str(18))
pan_up_left = '81 01 06 01 VV WW 01 01 FF'.replace('VV', str(18))
pan_up_right = '81 01 06 01 VV WW 02 01 FF'.replace('VV', str(18))
pan_down_left = '81 01 06 01 VV WW 01 02 FF'.replace('VV', str(18))
pan_down_right = '81 01 06 01 VV WW 02 02 FF'.replace('VV', str(18))
pan_stop = '81 01 06 01 VV WW 03 03 FF'.replace('VV', str(18))
#pan_absolute_position = '81 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV)) #YYYY[0]
#pan_relative_position = '81 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV))
pan_home = '81 01 06 04 FF'
pan_reset = '81 01 06 05 FF'

focus_stop = '81 01 04 08 00 FF'
focus_far = '81 01 04 08 02 FF'
focus_near = '81 01 04 08 03 FF'
focus_far_variable = '81 01 04 08 2p FF'.replace('p', '7') # 0 low to 7 high
focus_near_variable = '81 01 04 08 3p FF'.replace('p', '7') # 0 low to 7 high
focus_direct = '81 01 04 48 0p 0q 0r 0s FF' #.replace('p', ) q, r, s
focus_auto = '81 01 04 38 02 FF'
focus_manual = '81 01 04 38 03 FF'
focus_infinity = '81 01 04 18 02 FF'

class Camera:
    from time import sleep
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sequence_number = 1
    panSpeed = 7 # 1 to 18
    tiltSpeed = 7 # 1 to 17
    zoomSpeed = 7 # 0 to 7

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.reset_sequence_number()

    def send_bytes(self, message_bytes):
        payload_type = bytearray.fromhex('01 00')
        payload = bytearray.fromhex(message_bytes)
        payload_length = len(payload).to_bytes(2, 'big')
        message = payload_type + payload_length + self.sequence_number.to_bytes(4, 'big') + payload
        self.s.sendto(message, (self.ip, self.port))
        self.sequence_number += 1

    def send(self, message):
        message_bytes = ''  # translate message to bytes
        payload_type = bytearray.fromhex('01 00')
        payload = bytearray.fromhex(message_bytes)
        payload_length = len(payload).to_bytes(2, 'big')
        message = payload_type + payload_length + self.sequence_number.to_bytes(4, 'big') + payload
        self.s.sendto(message, (self.ip, self.port))
        self.sequence_number += 1
        self.send_bytes(message)

    def reset_sequence_number(self):
        message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
        self.s.sendto(message,(self.ip, self.port))
        self.sequence_number = 1
    
    def panTiltSpeed(self, panSpeed, tiltSpeed):
        if panSpeed > 0 and panSpeed <19:
            self.panSpeed = panSpeed
        self.tiltSpeed = tiltSpeed

    def multiply(self, x, y):
        print(x*y)
        return x * y
    
    def disconnect(self):
        self.s.close()