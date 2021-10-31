import socket
import binascii
import time


class ViscaException(RuntimeError):
    """Raised when the camera doesn't like a message that it received"""
    pass


ACK_RESPONSES = ['0f01', '9041ff']


class Camera:
    def __init__(self, ip, port=52381):
        self._location = (ip, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('', port))
        self._sock.settimeout(0.1)

        self.num_timeouts = 0
        self.sequence_number = 0
        self.reset_sequence_number()
        self._send_command('00 01')  # clear the camera's interface socket

    def _send_command(self, command_hex):
        payload_type = b'\x01\x00'
        preamble = b'\x81\x01'
        terminator = b'\xff'

        payload_bytes = preamble + bytearray.fromhex(command_hex) + terminator
        payload_length = len(preamble + payload_bytes + terminator).to_bytes(2, 'big')
        sequence_bytes = self.sequence_number.to_bytes(4, 'big')

        message = payload_type + payload_length + sequence_bytes + payload_bytes

        self._sock.sendto(message, self._location)

        ack_response = None
        completion_response = None

        while True:
            try:
                response = self._sock.recv(32)
                response_sequence_number = int.from_bytes(response[4:8], 'big')

                if response_sequence_number < self.sequence_number:
                    continue
                elif ack_response is None:
                    ack_response = response[8:]
                else:
                    completion_response = response[8:]
                    break

            except socket.timeout:  # Occasionally we don't get a response because this is UDP
                self.num_timeouts += 1
                break

        self.sequence_number += 1  # TODO wrap

    def reset_sequence_number(self):
        message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
        self._sock.sendto(message, self._location)
        self._sock.recv(32)
        self.sequence_number = 1

    def on(self):
        self._send_command('04 00 02')
    
    def off(self):
        self._send_command('04 00 03')

    def info_display_on(self):
        self._send_command('7E 01 18 02')

    def info_display_off(self):
        self._send_command('7E 01 18 03')

    def pantilt(self, pan_speed: int, tilt_speed: int):
        """
        Commands the camera to pan and/or tilt at the given speeds and directions.

        :param pan_speed: -24 to 24 where negative numbers cause a left pan and 0 causes panning to stop
        :param tilt_speed: -24 to 24 where negative numbers cause a downward tilt and 0 causes tilting to stop
        """
        payload_start = '06 01'

        if abs(pan_speed) > 24 or abs(tilt_speed) > 24:
            raise ValueError('pan_speed and tilt_speed must be between -24 and 24 inclusive')

        pan_speed_hex = f'{abs(pan_speed):02x}'
        tilt_speed_hex = f'{abs(tilt_speed):02x}'

        direction_hex = ''
        for speed in [pan_speed, tilt_speed]:
            if speed > 0:
                direction_hex += ' 01'
            elif speed < 0:
                direction_hex += ' 02'
            else:
                direction_hex += ' 03'

        self._send_command(payload_start + pan_speed_hex + tilt_speed_hex + direction_hex)

    def pantilt_stop(self):
        self.pantilt(0, 0)

    def pantilt_home(self):
        self._send_command('06 04')
    
    def pantilt_reset(self):
        self._send_command('06 05')

    def zoom_in(self):
        self.send('81 01 04 07 02 FF')

    def zoom_out(self):
        self.send('81 01 04 07 03 FF')
    
    def zoom_stop(self):
        self.zoom(0)

    def zoom(self, speed: int):
        """
        Zooms out or in at the given speed.
        :param speed: -7 to 7 where positive numbers zoom in and zero stops the zooming
        """
        if abs(speed) > 7:
            raise ValueError('The zoom speed must be -7 to 7 inclusive')

        speed_hex = f'{abs(speed):x}'

        if speed == 0:
            direction_hex = '0'
        elif speed > 0:
            direction_hex = '2'
        else:
            direction_hex = '3'

        self._send_command(f'04 07 {direction_hex}{speed_hex}')
    
    def zoom_to(self, position: float):  # 0 <= zoom position <= 16384
        """
        Zooms to an absolute position
        :param position: 0-1, where 1 is zoomed all the way in
        """
        position_int = round(position * 16384)
        position_hex = f'{position_int:04x}'

        payload = '04 47'
        for hex_char in position_hex:
            payload += f' 0{hex_char}'

        self._send_command(payload)

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
    
    def focus_near_variable(self, speed):  # 0 low to 7 high
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
        memory_hex = str(hex(memory_number)[2:])
        self.send('81 01 04 3F 00 0'+memory_hex+' FF')

    def inquiry_zoom_position(self):
        self.send('81 09 04 47 FF')
    
    def inquiry_focus_position(self):
        self.send('81 09 04 48 FF')

    def inquiry_pantilt_position(self):
        self.send('81 09 06 12 FF')

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