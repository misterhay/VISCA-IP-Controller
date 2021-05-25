
class Camera:
    from time import sleep
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sequence_number = 1
    panSpeed = 7 # 1 to 18
    tiltSpeed = 7 # 1 to 17
    zoomSpeed = 7 # 0 to 7

    # for receiving
    #buffer_size = 1024
    #s.bind(('', camera_port)) # use the port one higher than the camera's port
    #s.settimeout(1) # only wait for a response for 1 second

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

    def pan(self, direction, pan_speed, tilt_speed):
        try:
            if 1 <= pan_speed <= 9:
                pan_speed_hex = '0'+str(pan_speed)
            if 10 <= pan_speed <= 18:
                pan_speed_hex = str(hex(pan_speed)[2:])
        except:
            pan_speed_hex = '00'
        try:
            if 1 <= tilt_speed <= 9:
                tilt_speed_hex = '0'+str(pan_speed)
            if 10 <= tilt_speed <= 17:
                tilt_speed_hex = str(hex(pan_speed)[2:])
        except:
            tilt_speed_hex = '00'
        if direction == 'up':
            message = '81 01 06 01 VV WW 03 01 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'down':
            message = '81 01 06 01 VV WW 03 02 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'left':
            message = '81 01 06 01 VV WW 01 03 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'right':
            message = '81 01 06 01 VV WW 02 01 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'upleft':
            message = '81 01 06 01 VV WW 01 01 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'upright':
            message = '81 01 06 01 VV WW 02 01 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'downleft':
            message = '81 01 06 01 VV WW 01 02 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'downright':
            message = '81 01 06 01 VV WW 02 02 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'stop':
            message = '81 01 06 01 VV WW 03 03 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        self.send(message)

    def pan_stop(self):
        self.send('81 01 06 01 00 00 03 03 FF')

    def pan_home(self):
        self.send('81 01 06 04 FF')
    
    def pan_reset(self):
        self.send('81 01 06 05 FF')
    
    def pan_absolute(self, pan_angle, tilt_angle, pan_speed, tilt_speed): # Pan Position 56832 (DE00) to 8704 (2200) (CENTER 0000)
        try:
            if 1 <= pan_speed <= 9:
                pan_speed_hex = '0'+str(pan_speed)
            if 10 <= pan_speed <= 18:
                pan_speed_hex = str(hex(pan_speed)[2:])
        except:
            pan_speed_hex = '00'
        try:
            if 1 <= tilt_speed <= 9:
                tilt_speed_hex = '0'+str(pan_speed)
            if 10 <= tilt_speed <= 17:
                tilt_speed_hex = str(hex(pan_speed)[2:])
        except:
            tilt_speed_hex = '00'
        # YYYY: Pan Position DE00 to 2200 (CENTER 0000)
        # ZZZZ: Tilt Position FC00 to 1200 (CENTER 0000)
        #YYYY = '0000'
        #ZZZZ = '0000'
        #pan_absolute_position = '81 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV)) #YYYY[0]
        #pan_relative_position = '81 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV))

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

    def recall(self, memory_number):
        self.info_display_off() # otherwise we see a message on the camera output
        self.sleep(0.25)
        memory_hex = str(hex(memory_number)[2:])
        self.send('81 01 04 3F 02 0'+memory_hex+' FF')
        self.sleep(1)
        self.info_display_off() # to make sure it doesn't display "done"

    def memory_set(self, memory_number):
        memory_hex = hex(memory_number)[-1]
        self.send('81 01 04 3F 02 0p FF'.replace('p', memory_hex))
    
    def memory_reset(self, memory_number):
        memory_hex = str(hex(memory_number)[2:])
        self.send('81 01 04 3F 00 0'+memory_hex+' FF')
    
    def save_preset_labels(self):
        with open('preset_labels.txt', 'w') as f:
            for entry in self.entry_boxes:
                f.write(entry.get())
                f.write('\n')
        f.close()