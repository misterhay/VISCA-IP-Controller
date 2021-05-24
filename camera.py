
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

    def disconnect(self):
        self.s.close()

    '''
    def send_bytes(self, message_bytes):
        payload_type = bytearray.fromhex('01 00')
        payload = bytearray.fromhex(message_bytes)
        payload_length = len(payload).to_bytes(2, 'big')
        message = payload_type + payload_length + self.sequence_number.to_bytes(4, 'big') + payload
        self.s.sendto(message, (self.ip, self.port))
        #self.sequence_number += 1
    #'''

    def send(self, message):
        #message_bytes = ''  # translate message to bytes
        payload_type = bytearray.fromhex('01 00')
        payload = bytearray.fromhex(message)
        payload_length = len(payload).to_bytes(2, 'big')
        message = payload_type + payload_length + self.sequence_number.to_bytes(4, 'big') + payload
        self.s.sendto(message, (self.ip, self.port))
        self.sequence_number += 1
        #self.send_bytes(message)

    def reset_sequence_number(self):
        message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
        self.s.sendto(message,(self.ip, self.port))
        self.sequence_number = 1

    def on(self):
        self.send('81 01 04 00 02 FF')
    
    def off(self):
        self.send('81 01 04 00 03 FF')

    def info_display_on(self):
        self.send('81 01 7E 01 18 02 FF')

    def info_display_off(self):
        self.send('81 01 7E 01 18 03 FF')
    
    #def set_pan_tilt_speed(self, pan_speed, tilt_speed):
    #    if pan_speed > 0 and pan_speed < 19:
    #        self.pan_speed = pan_speed
    #    self.tilt_speed = tilt_speed

    def zoom_in(self):
        self.send('81 01 04 07 02 FF')

    def zoom_out(self):
        self.send('81 01 04 07 03 FF')
    
    def zoom_stop(self):
        self.send('81 01 04 07 00 FF')

    def zoom_in_speed(self, speed): # speed=0 (Low) to 7 (High)
        try:
            if 0 <= speed <= 7:
                pass
            else:
                speed = 0
        except:
            speed = 0
        self.send('81 01 04 07 2'+str(speed)+' FF')
    
    def zoom_out_speed(self, speed): # speed=0 (Low) to 7 (High)
        try:
            if 0 <= speed <= 7:
                pass
            else:
                speed = 0
        except:
            speed = 0
        self.send('81 01 04 07 3'+str(speed)+' FF')
        print(speed)

    def zoom_to(self, position): # 0 <= zoom position <= 16384
        try:
            if 0 <= position <= 16384:
                x = str(hex(position)[2:])
                self.send('81 01 04 47 0'+x[0]+' 0'+x[1]+' 0'+x[2]+' 0'+x[3]+' FF')
        except:
            pass
        
    def focus_auto(self):
        self.send('81 01 04 38 02 FF')

    def focus_manual(self):
        self.send('81 01 04 38 03 FF')

    def focus_infinity(self):
        self.send('81 01 04 18 02 FF')

    def focus_near(self):
        self.send('81 01 04 08 03 FF')
    
    def focus_far(self):
        self.send('81 01 04 08 02 FF')
    
    def focus_stop(self):
        self.send('81 01 04 08 00 FF')
    
    def focus_near_variable(self, speed): # 0 low to 7 high
        try:
            if 0 <= speed <= 7:
                pass
            else:
                speed = 0
        except:
            speed = 0
        self.send('81 01 04 08 2'+str(speed)+' FF')
    
    def focus_far_variable(self, speed): # 0 low to 7 high
        try:
            if 0 <= speed <= 7:
                pass
            else:
                speed = 0
        except:
            speed = 0
        self.send('81 01 04 08 3'+str(speed)+' FF')

    def focus_to(self, position): # infinity = 0, 0.08m = 16
        try:
            if 0 <= position <= 16:
                x = str(hex(position)[2:])
                self.send('81 01 04 47 0'+x+' 00 00 00 FF')
        except:
            pass
    
    def focus_one_push(self):
        self.send('81 01 04 18 01 FF')

    def autofocus_mode(self, mode): # 'normal', 'interval', 'zoom'
        if mode == 'normal':
            self.send('81 01 04 57 00 FF')
        if mode == 'interval':
            self.send('81 01 04 57 01 FF')
        if mode == 'zoom':
            self.send('81 01 04 57 02 FF')
        
    def autofocus_interval(self, operating, staying):
        try:
            self.send('81 01 04 57 02 FF') # set mode to interval
            if 0 <= operating <= 255 and 0 <= staying <= 255:
                x = str(hex(operating)[2:])
                y = str(hex(staying)[2:])
                self.send('81 01 04 27 0'+x[0]+' 0'+x[1]+' 0'+y[0]+' 0'+y[1]+' FF')
        except:
            pass
    
    def autofocus_sensitivity(self, sensitivity): # normal or low
        if sensitivity == 'low':
            self.send('81 01 04 58 03 FF')
        else:
            self.send('81 01 04 58 02 FF')
