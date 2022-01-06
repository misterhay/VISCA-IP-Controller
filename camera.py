class Camera:
    from time import sleep
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # for receiving, prevent TIME_WAIT state
    import binascii # for translating received messages

    
    sequence_number = 1

    ## Messages:
    ## 81 0q 0r ... FF
    ## q = 1 for command, q = 9 for inquiry
    ## r = 4 for camera, r = 6 for pan/tilt

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.s.bind(('', port)) # for receiving
        self.reset_sequence_number()
    
    def connect(self):
        self.send('81 01 00 01 FF') # clear the camera's interface socket
        self.reset_sequence_number()

    def disconnect(self):
        self.s.close()

    def send(self, message):
        payload_type = bytearray.fromhex('01 00')
        payload = bytearray.fromhex(message)
        payload_length = len(payload).to_bytes(2, 'big')
        message = payload_type + payload_length + self.sequence_number.to_bytes(4, 'big') + payload
        self.s.sendto(message, (self.ip, self.port))
        self.sequence_number += 1
        #print(message)
        data = self.s.recv(1024)
        print(data)

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

    def pantilt(self, direction, pan_speed, tilt_speed):
        try:
            if 1 <= pan_speed <= 24:
                pan_speed_hex = str(hex(pan_speed)[2:])
            else:
                pan_speed_hex = '00'
            if len(pan_speed_hex) == 1:
                pan_speed_hex = '0'+pan_speed_hex
        except:
            pan_speed_hex = '00'
        try:
            if 1 <= tilt_speed <= 15:
                tilt_speed_hex = '0'+str(hex(tilt_speed)[2:])
            elif 16 <= tilt_speed <= 24:
                tilt_speed_hex = str(hex(tilt_speed)[2:])
            else:
                tilt_speed_hex = '00'
        except:
            tilt_speed_hex = '00'
        if direction == 'up':
            message = '81 01 06 01 VV WW 03 01 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'down':
            message = '81 01 06 01 VV WW 03 02 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'left':
            message = '81 01 06 01 VV WW 01 03 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
        if direction == 'right':
            message = '81 01 06 01 VV WW 02 03 FF'.replace('VV', pan_speed_hex).replace('WW', tilt_speed_hex)
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

    def pantilt_stop(self):
        self.send('81 01 06 01 00 00 03 03 FF')

    def pantilt_home(self):
        self.send('81 01 06 04 FF')
    
    def pantilt_reset(self):
        self.send('81 01 06 05 FF')
    '''
    def pantilt_absolute(self, pan_angle, tilt_angle, pan_speed, tilt_speed): # Pan Position 56832 (DE00) to 8704 (2200) (CENTER 0000)
        try:
            if 1 <= pan_speed <= 15:
                pan_speed_hex = '0'+str(hex(pan_speed)[2:])
            if 16 <= pan_speed <= 24:
                pan_speed_hex = str(hex(pan_speed)[2:])
        except:
            pan_speed_hex = '00'
        try:
            if 1 <= tilt_speed <= 15:
                tilt_speed_hex = '0'+str(hex(pan_speed)[2:])
            if 16 <= tilt_speed <= 23:
                tilt_speed_hex = str(hex(pan_speed)[2:])
        except:
            tilt_speed_hex = '00'
        if pan_angle < 0:
            pan_direction = 'F'
        else:
            pan_direction = '0'
        if tilt_angle < 0:
            tilt_direction = 'F'
        else:
            tilt_direction = '0'
        
        # YYYY: Pan Position DE00 to 2200 (CENTER 0000)
        # ZZZZ: Tilt Position FC00 to 1200 (CENTER 0000)
        #YYYY = '0000'
        #ZZZZ = '0000'
        #pan_absolute_position = '81 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV)) #YYYY[0]
        #pan_relative_position = '81 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV))
    #'''

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

    def memory_recall(self, memory_number):
        self.info_display_off() # otherwise we see a message on the camera output
        self.sleep(0.25)
        memory_hex = str(hex(memory_number)[2:])
        self.send('81 01 04 3F 02 0'+memory_hex+' FF')
        self.sleep(1)
        self.info_display_off() # to make sure it doesn't display "done"

    def memory_set(self, memory_number): # 8x 01 04 3F 01 0p FF
        memory_hex = hex(memory_number)[-1]
        self.send('81 01 04 3F 01 0p FF'.replace('p', memory_hex))
    
    def memory_reset(self, memory_number):
        memory_hex = hex(memory_number)[-1]
        self.send('81 01 04 3F 00 0'+memory_hex+' FF')

    def white_balance(self, mode):
        modes = {'auto':'1', 'indoor':'2', 'outdoor':'3', 'one push':'4', 'manual':'5', 'outdoor auto':'6', 'sodium lamp auto':'7', 'sodium auto':'8'}
        self.send('81 01 04 35 0'+modes[mode]+' FF')
    
    def gain(self, mode):
        try:
            if 0 <= mode <= 255:
                mode_hex = format(mode, '02x')
                self.send('81 01 04 0C 00 00 0'+mode_hex[0]+' 0'+mode_hex[1]+' FF')
        except:
            if mode == 'reset':
                self.send('81 01 04 0C 00 FF')
            elif mode == 'up':
                self.send('81 01 04 0C 02 FF')
            elif mode == 'down':
                self.send('81 01 04 0C 03 FF')
            else:
                pass
    
    def rgain(self, gain): # reset, up, down, or direct (0 to 255)
        if gain == 'reset':
            self.send('81 01 04 03 00 FF')
        elif gain == 'up':
            self.send('81 01 04 03 02 FF')
        elif gain == 'down':
            self.send('81 01 04 03 03 FF')
        else:
            try:
                if 0 <= gain <= 255:
                    gain_hex = format(gain, '02x')
                    self.send('81 01 04 43 00 00 0'+gain_hex[0]+' 0'+gain_hex[1]+' FF')
            except:
                pass

    def bgain(self, gain): # reset, up, down, or direct (0 to 255)
        if gain == 'reset':
            self.send('81 01 04 04 00 FF')
        elif gain == 'up':
            self.send('81 01 04 04 02 FF')
        elif gain == 'down':
            self.send('81 01 04 04 03 FF')
        else:
            try:
                if 0 <= gain <= 255:
                    gain_hex = format(gain, '02x')
                    self.send('81 01 04 44 00 00 0'+gain_hex[0]+' 0'+gain_hex[1]+' FF')
            except:
                pass

    def color_gain(self, color, gain): # gain from -4 to +10
        try:
            channel_map = {'master':'0','magenta':'1','red':'2','yellow':'3','green':'4','cyan':'5','blue':'6'}
            if color in channel_map.keys():
                color = channel_map[color]
            else:
                color = '0'
            if -4 <= gain <= 10:
                gain_hex = hex(gain+4)[-1] # to map -4 to +10 to 0 to 15
                self.send('81 01 04 49 00 00 0'+color+' 0'+gain_hex+' FF')
        except:
            pass

    def autoexposure(self, mode):
        modes = {'auto':'0', 'manual':'3', 'bright':'D'}
        self.send('81 01 04 39 0'+modes[mode]+' FF')
    
    def shutter(self, mode): # reset, up, down, or direct (0 to 255)
        try:
            if 0 <= mode <= 255:
                mode_hex = format(mode, '02x')
                self.send('81 01 04 0A 00 00 0'+mode_hex[0]+' 0'+mode_hex[1]+' FF')
        except:
            if mode == 'reset':
                self.send('81 01 04 0A 00 FF')
            elif mode == 'up':
                self.send('81 01 04 0A 02 FF')
            elif mode == 'down':
                self.send('81 01 04 0A 03 FF')
            else:
                pass
    
    def iris(self, mode):
        try:
            if 0 <= mode <= 255:
                mode_hex = format(mode, '02x')
                self.send('81 01 04 4B 00 00 0'+mode_hex[0]+' 0'+mode_hex[1]+' FF')
        except:
            if mode == 'reset':
                self.send('81 01 04 0B 00 FF')
            elif mode == 'up':
                self.send('81 01 04 0B 02 FF')
            elif mode == 'down':
                self.send('81 01 04 0B 03 FF')
            else:
                pass

    def brightness(self, mode):
        try:
            if 0 <= mode <= 255:
                mode_hex = format(mode, '02x')
                self.send('81 01 04 4D 00 00 0'+mode_hex[0]+' 0'+mode_hex[1]+' FF')
        except:
            if mode == 'reset':
                self.send('81 01 04 0D 00 FF')
            elif mode == 'up':
                self.send('81 01 04 0D 02 FF')
            elif mode == 'down':
                self.send('81 01 04 0D 03 FF')
            else:
                pass

    def exposure_compensation(self, mode):
        try:
            if 0 <= mode <= 255:
                mode_hex = format(mode, '02x')
                self.send('81 01 04 4E 00 00 0'+mode_hex[0]+' 0'+mode_hex[1]+' FF')
        except:
            if mode == 'reset':
                self.send('81 01 04 0E 00 FF')
            elif mode == 'up':
                self.send('81 01 04 0E 02 FF')
            elif mode == 'down':
                self.send('81 01 04 0E 03 FF')
            elif mode == 'on':
                self.send('81 01 04 3E 02 FF')
            elif mode == 'off':
                self.send('81 01 04 3E 03 FF')
            else:
                pass

    def backlight(self, mode):
        modes = {'on':'2', 'off':'3'}
        self.send('81 01 04 33 0'+modes[mode]+' FF')
    
    def aperature(self, mode):
        try:
            if 0 <= mode <= 255:
                mode_hex = format(mode, '02x')
                self.send('81 01 04 42 00 00 0'+mode_hex[0]+' 0'+mode_hex[1]+' FF')
        except:
            if mode == 'reset':
                self.send('81 01 04 02 00 FF')
            elif mode == 'up':
                self.send('81 01 04 02 02 FF')
            elif mode == 'down':
                self.send('81 01 04 02 03 FF')
            else:
                pass
    
    def mirror(self, mode):
        modes = {'on':'2', 'off':'3'}
        self.send('81 01 04 61 0'+modes[mode]+' FF')
    
    def flip(self, mode):
        modes = {'on':'2', 'off':'3'}
        self.send('81 01 04 66 0'+modes[mode]+' FF')
    
    def mount_mode(self, mode):
        modes = {'up':'2', 'down':'3'}
        self.send('81 01 04 A4 0'+modes[mode]+' FF')

    def noise_reduction_2d(self, amount):
        try:
            if 0 <= amount <= 5:
                self.send('81 01 04 53 0'+str(amount)+' FF')
        except:
            pass
    
    def noise_reduction_3d(self, amount):
        try:
            if 0 <= amount <= 3:
                self.send('81 01 04 54 0'+str(amount)+' FF')
        except:
            pass

    def freeze(self, mode):
        modes = {'on':'02', 'off':'03', 'preset_on':'22', 'preset_off':'23'}
        self.send('81 01 04 62 '+modes[mode]+' FF')

    def inquiry_zoom_position(self):
        self.send('81 09 04 47 FF')
    
    def inquiry_focus_position(self):
        self.send('81 09 04 48 FF')

    def inquiry_pantilt_position(self):
        self.send('81 09 06 12 FF')

    # TODO: other inquiry commands

'''
## Messages from Camera
90 50 FF      Interface cleared
90 4y FF      Acknowledge
90 5y FF      Complete
90 5Y ... FF  Inquiry Response
y = socket number

## Inquiry Responses
y0 50 0p 0q 0r 0s FF  Zoom or Focus Position
y0 50 0w 0w 0w 0w 0z 0z 0z 0z FF  wwww = Pan Position, zzzz = Tilt Position
y = socket number

## Errors
90 6y 01 FF  Message length error
90 60 02 FF  Syntax Error
90 60 03 FF  Command buffer full
90 6y 04 FF  Command canceled
90 6y 05 FF  No socket (to be canceled)
90 6y 41 FF  Command not executable
y = socket number

'''