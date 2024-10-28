import socket
from typing import Optional, Tuple

from visca_over_ip.exceptions import ViscaException, NoQueryResponse

SEQUENCE_NUM_MAX = 2 ** 32 - 1


class Camera:
    """
    Represents a camera that has a VISCA-over-IP interface.
    Provides methods to control a camera over that interface.

    Only one camera can be connected on a given port at a time.
    If you wish to use multiple cameras, you will need to switch between them (use :meth:`close_connection`)
    or set them up to use different ports.
    """
    def __init__(self, ip: str, port=52381):
        """:param ip: the IP address or hostname of the camera you want to talk to.
        :param port: the port number to use. 52381 is the default for most cameras.
        """
        self._location = (ip, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # for UDP stuff
        self._sock.bind(('', 0))
        self._port = self._sock.getsockname()[1]  
        self._sock.settimeout(0.1)

        self.num_missed_responses = 0
        self.sequence_number = 0  # This number is encoded in each message and incremented after sending each message
        self.num_retries = 5
        self.reset_sequence_number()
        try:
            self._send_command('00 01')  # clear the camera's interface socket
        except ViscaException as exc:
            print(f"Could not clear the camera's interface socket: {exc}")

    def _send_command(self, command_hex: str, query=False) -> Optional[bytes]:
        """Constructs a message based ong the given payload, sends it to the camera,
        and blocks until an acknowledge or completion response has been received.
        :param command_hex: The body of the command as a hex string. For example: "00 02" to power on.
        :param query: Set to True if this is a query and not a standard command.
            This affects the message preamble and also ensures that a response will be returned and not None
        :return: The body of the first response to the given command as bytes
        """
        payload_type = b'\x01\x00'
        preamble = b'\x81' + (b'\x09' if query else b'\x01')
        terminator = b'\xff'

        payload_bytes = preamble + bytearray.fromhex(command_hex) + terminator
        payload_length = len(payload_bytes).to_bytes(2, 'big')

        exception = None
        for retry_num in range(self.num_retries):
            self._increment_sequence_number()
            sequence_bytes = self.sequence_number.to_bytes(4, 'big')
            message = payload_type + payload_length + sequence_bytes + payload_bytes

            self._sock.sendto(message, self._location)

            try:
                response = self._receive_response()
            except ViscaException as exc:
                exception = exc
            else:
                if response is not None:
                    return response[1:-1]
                elif not query:
                    return None
        if exception:
            raise exception
        else:
            raise NoQueryResponse(f'Could not get a response after {self.num_retries} tries')

    def _receive_response(self) -> Optional[bytes]:
        """Attempts to receive the response of the most recent command.
        Sometimes we don't get the response because this is UDP.
        In that case we just increment num_missed_responses and move on.
        :raises ViscaException: if the response is an error and not an acknowledge or completion
        """
        while True:
            try:
                response = self._sock.recv(32)
                response_sequence_number = int.from_bytes(response[4:8], 'big')

                if response_sequence_number < self.sequence_number:
                    continue
                else:
                    response_payload = response[8:]
                    if len(response_payload) > 2:
                        status_byte = response_payload[1]
                        if status_byte >> 4 not in [5, 4]:
                            raise ViscaException(response_payload)
                        else:
                            return response_payload

            except socket.timeout:  # Occasionally we don't get a response because this is UDP
                self.num_missed_responses += 1
                break

    def reset_sequence_number(self):
        message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
        self._sock.sendto(message, self._location)
        self._receive_response()
        self.sequence_number = 1

    def _increment_sequence_number(self):
        self.sequence_number += 1
        if self.sequence_number > SEQUENCE_NUM_MAX:
            self.sequence_number = 0

    def close_connection(self):
        """Only one camera can be bound to a socket at once.
        If you want to connect to another camera which uses the same communication port,
        first call this method on the first camera.
        """
        self._sock.close()

    def set_power(self, power_state: bool):
        """Powers on or off the camera based on the value of power_state"""
        for _ in range(4):
            try:
                if power_state:
                    self._send_command('04 00 02')
                else:
                    self._send_command('04 00 03')

            except ViscaException as exc:
                if exc.status_code != 0x41:
                    raise exc

    def info_display(self, display_mode: bool):
        """Sets the information display mode of the camera
        :param display_mode: True for on, False for off
        """
        if display_mode:
            self._send_command('7E 08 18 02')
        else:
            self._send_command('7E 08 18 03')

    def pantilt(self, pan_speed: int, tilt_speed: int, pan_position=None, tilt_position=None, relative=False):
        """Commands the camera to pan and/or tilt.
        You must specify both pan_position and tilt_position OR specify neither

        :param pan_speed: -24 to 24 where negative numbers cause a right pan, 0 causes panning to stop,
            and positive numbers cause a left pan
        :param tilt_speed: -24 to 24 where negative numbers cause a downward tilt, 0 causes tilting to stop,
            and positive numbers cause an upward tilt.
        :param pan_position: if specified, the camera will move this distance or go to this absolute position
            depending on the value of `relative`.
            Should be a signed integer where 0 is the center of the range.
            The camera will stop panning when numbers reach a high enough magnitude, but will not wrap around.
            The pan limits are different for different models of camera and can be tightened by the user.
        :param tilt_position: if specified, the camera will move this distance or go to this absolute position
            depending on the value of `relative`.
            The camera will stop tilting when number reach a high enough magnitude, but will not wrap around.
            The tilt limits are different for different models of camera and can be tightened by the user.
        :param relative: If set to True, the position will be relative instead of absolute.

        :raises ViscaException: if invalid values are specified for positions
        :raises ValueError: if invalid values are specified for speeds
        """
        speed_params = [pan_speed, tilt_speed]
        position_params = [pan_position, tilt_position]
        if position_params.count(None) == 1:
            raise ValueError('You must specify both pan_position and tilt_position or nether')

        if abs(pan_speed) > 24 or abs(tilt_speed) > 24:
            raise ValueError('pan_speed and tilt_speed must be between -24 and 24 inclusive')

        if not all(isinstance(param, int) or param is None for param in speed_params + position_params):
            raise ValueError('All parameters must be integers or None')

        pan_speed_hex = f'{abs(pan_speed):02x}'
        tilt_speed_hex = f'{abs(tilt_speed):02x}'

        if None not in position_params:
            def encode(position: int):
                """Converts a signed integer to hex with each nibble seperated by a 0"""
                pos_hex = position.to_bytes(2, 'big', signed=True).hex()
                return ' '.join(['0' + char for char in pos_hex])

            relative_hex = '03' if relative else '02'

            self._send_command(
                '06' + relative_hex + pan_speed_hex + tilt_speed_hex + encode(pan_position) + encode(tilt_position)
            )

        else:
            payload_start = '06 01'

            def get_direction_hex(speed: int):
                if speed < 0:
                    return '01'
                if speed > 0:
                    return '02'
                else:
                    return '03'

            self._send_command(
                payload_start + pan_speed_hex + tilt_speed_hex +
                get_direction_hex(pan_speed) + get_direction_hex(tilt_speed)
            )

    def pantilt_home(self):
        """Moves the camera to the home position"""
        self._send_command('06 04')

    def pantilt_reset(self):
        """Moves the camera to the reset position"""
        self._send_command('06 05')

    def zoom(self, speed: int):
        """Zooms out or in at the given speed.

        :param speed: -7 to 7 where positive numbers zoom in, zero stops the zooming, and negative numbers zoom out.
        """
        if not isinstance(speed, int) or abs(speed) > 7:
            raise ValueError('The zoom speed must be an integer from -7 to 7 inclusive')

        speed_hex = f'{abs(speed):x}'

        if speed == 0:
            direction_hex = '0'
        elif speed > 0:
            direction_hex = '2'
        else:
            direction_hex = '3'

        self._send_command(f'04 07 {direction_hex}{speed_hex}')
    
    def zoom_to(self, position: float):
        """Zooms to an absolute position

        :param position: 0-1, where 1 is zoomed all the way in
        """
        position_int = round(position * 16384)
        position_hex = f'{position_int:04x}'
        self._send_command('04 47 ' + ''.join(['0' + char for char in position_hex]))

    def digital_zoom(self, digital_zoom_state: bool):
        """Sets the digital zoom state of the camera
        :param digital_zoom_state: True for on, False for off
        """
        if digital_zoom_state:
            self._send_command('04 06 02')
        else:
            self._send_command('04 06 03')

    def increase_exposure_compensation(self):
        self._send_command('04 0E 02')

    def decrease_exposure_compensation(self):
        self._send_command('04 0E 03')

    def set_focus_mode(self, mode: str):
        """Sets the focus mode of the camera

        :param mode: One of "auto", "manual", "auto/manual", "one push trigger", or "infinity".
            See the manual for an explanation of these modes.
        """
        modes = {
            'auto': '38 02',
            'manual': '38 03',
            'auto/manual': '38 10',
            'one push trigger': '18 01',
            'infinity': '18 02'
        }

        mode = mode.lower()
        if mode not in modes:
            raise ValueError(f'"{mode}" is not a valid mode. Valid modes: {", ".join(modes.keys())}')

        self._send_command('04 ' + modes[mode])

    def set_autofocus_mode(self, mode: str):
        """Sets the autofocus mode of the camera
        :param mode: One of "normal", "interval", or "one push trigger".
            See the manual for an explanation of these modes.
        """
        modes = {
            'normal': '0',
            'interval': '1',
            'zoom trigger': '2'
        }

        mode = mode.lower()
        if mode not in modes:
            raise ValueError(f'"{mode}" is not a valid mode. Valid modes: {", ".join(modes.keys())}')

        self._send_command('04 57 0' + modes[mode])

    def set_autofocus_interval(self, active_time: int, interval_time: int):
        """Sets the autofocus interval of the camera
        :param active_time in seconds, interval_time in seconds.
        """
        if interval_time < 1 or interval_time > 255 or active_time < 1 or active_time > 255:
            raise ValueError('The time must be between 1 and 255 seconds')

        self._send_command('04 27 ' + f'{active_time:02x}' +' '+ f'{interval_time:02x}')

    def autofocus_sensitivity_low(self, sensitivity_low: bool):
        """Sets the sensitivity of the autofocus to low
        :param sensitivity_low: True for on, False for off
        """
        if sensitivity_low:
            self._send_command('04 58 03')
        else:
            self._send_command('04 58 02')

    def manual_focus(self, speed: int):
        """Focuses near or far at the given speed.
        Set the focus mode to manual before calling this method.

        :param speed: -7 to 7 where positive integers focus near and negative integers focus far
        """
        if not isinstance(speed, int) or abs(speed) > 7:
            raise ValueError('The focus speed must be an integer from -7 to 7 inclusive')

        speed_hex = f'{abs(speed):x}'

        if speed == 0:
            direction_hex = '0'
        elif speed > 0:
            direction_hex = '3'
        else:
            direction_hex = '2'

        self._send_command(f'04 08 {direction_hex}{speed_hex}')

    def ir_correction(self, mode: bool):
        """Sets the focus IR correction mode of the camera
        :param value: True for IR correction mode, False for standard mode
        """
        if mode:
            self._send_command('04 11 01')
        else:
            self._send_command('04 11 00')

    def white_balance_mode(self, mode: str):
        """Sets the white balance mode of the camera
        :param mode: One of "auto", "indoor", "outdoor", "auto tracing", "manual", "color temperature", "one push", or "one push trigger".
            See the manual for an explanation of these modes.
        """
        modes = {
            'auto': '35 00',
            'indoor': '35 01',
            'outdoor': '35 02',
            'one push': '35 03',
            'auto tracing': '35 04',
            'manual': '35 05',
            'color temperature': '35 20',
            'one push trigger': '10 05'
        }

        mode = mode.lower()
        if mode not in modes:
            raise ValueError(f'"{mode}" is not a valid mode. Valid modes: {", ".join(modes.keys())}')

        self._send_command('04 ' + modes[mode])

    def set_red_gain(self, gain: int):
        """Sets the red gain of the camera
        :param gain: 0-255
        """
        if not isinstance(gain, int) or gain < 0 or gain > 255:
            raise ValueError('The gain must be an integer from 0 to 255 inclusive')

        self._send_command('04 43 00 00 ' + f'{gain:02x}')

    def increase_red_gain(self):
        self._send_command('04 03 02')

    def decrease_red_gain(self):
        self._send_command('04 03 03')

    def reset_red_gain(self):
        self._send_command('04 03 00')

    def set_blue_gain(self, gain: int):
        """Sets the blue gain of the camera
        :param gain: 0-255
        """
        if not isinstance(gain, int) or gain < 0 or gain > 255:
            raise ValueError('The gain must be an integer from 0 to 255 inclusive')

        self._send_command('04 44 00 00 ' + f'{gain:02x}')

    def increase_blue_gain(self):
        self._send_command('04 04 02')

    def decrease_blue_gain(self):
        self._send_command('04 03 03')

    def reset_blue_gain(self):
        self._send_command('04 04 00')

    def set_white_balance_temperature(self, temperature: int):
        """Sets the white balance temperature of the camera
        :param temperature: 0-255
        """
        if not isinstance(temperature, int) or temperature < 0 or temperature > 255:
            raise ValueError('The temperature must be an integer from 0 to 255 inclusive')

        self._send_command('04 43 00 20 ' + f'{temperature:02x}')

    def increase_white_balance_temperature(self):
        self._send_command('04 03 02')

    def decrease_white_balance_temperature(self):
        self._send_command('04 03 03')

    def reset_white_balance_temperature(self):
        self._send_command('04 03 00')

    def set_color_gain(self, color:str, gain: int):
        """Sets the color gain of the camera
        :param color: 'master', 'magenta', 'red', 'yellow', 'green', 'cyan', 'blue'
        :param gain: 0-15; initial value is 4
        """
        colors = {
            'master': '0',
            'magenta': '1',
            'red': '2',
            'yellow': '3',
            'green': '4',
            'cyan': '5',
            'blue': '6'
        }
        if color not in colors:
            raise ValueError(f'"{color}" is not a valid color. Valid colors: {", ".join(colors.keys())}')

        if not isinstance(gain, int) or gain < 0 or gain > 15:
            raise ValueError('The gain must be an integer from 0 to 15 inclusive')

        self._send_command('04 49 00 00 0' + colors[color] + f' {gain:02x}')

    def set_gain(self, gain: int):
        """Sets the gain of the camera
        :param gain: 0-255
        """
        if not isinstance(gain, int) or gain < 0 or gain > 255:
            raise ValueError('The gain must be an integer from 0 to 255 inclusive')

        self._send_command('04 4C 00 00 ' + f'{gain:02x}')

    def increase_gain(self):
        self._send_command('04 0C 02')
    
    def decrease_gain(self):
        self._send_command('04 0C 03')

    def reset_gain(self):
        self._send_command('04 0C 00')

    def autoexposure_mode(self, mode: str):
        """Sets the autoexposure mode of the camera
        :param mode: One of "auto", "manual", "shutter priority", "iris priority", or "bright".
            See the manual for an explanation of these modes.
        """
        modes = {
            'auto': '0',
            'manual': '3',
            'shutter priority': 'A',
            'iris priority': 'B',
            'bright': 'D'
        }
        mode = mode.lower()

        if mode not in modes:
            raise ValueError(f'"{mode}" is not a valid mode. Valid modes: {", ".join(modes.keys())}')

        self._send_command('04 39 0' + modes[mode])

    def set_shutter(self, shutter: int):
        """Sets the shutter of the camera
        :param shutter: 0-21
        """
        if not isinstance(shutter, int) or shutter < 0 or shutter > 21:
            raise ValueError('The shutter must be an integer from 0 to 21 inclusive')

        self._send_command('04 4A 00 ' + f'{shutter:02x}')

    def increase_shutter(self):
        self._send_command('04 0A 02')
    
    def decrease_shutter(self):
        self._send_command('04 0A 03')
    
    def reset_shutter(self):
        self._send_command('04 0A 00')

    def slow_shutter(self, mode: bool):
        """Sets the slow shutter mode of the camera
        :param mode: True for on, False for off
        """
        if mode:
            self._send_command('04 5A 02')
        else:
            self._send_command('04 5A 03')

    def set_iris(self, iris: int):
        """Sets the iris of the camera
        :param iris: 0-17
        """
        if not isinstance(iris, int) or iris < 0 or iris > 17:
            raise ValueError('The iris must be an integer from 0 to 17 inclusive')

        self._send_command('04 4B 00 00 ' + f'{iris:02x}')
    
    def increase_iris(self):
        self._send_command('04 0B 02')

    def decrease_iris(self):
        self._send_command('04 0B 03')

    def reset_iris(self):
        self._send_command('04 0B 00')

    def set_brightness(self, brightness: int):
        """Sets the brightness of the camera
        :param brightness: 0-255
        """
        if not isinstance(brightness, int) or brightness < 0 or brightness > 255:
            raise ValueError('The brightness must be an integer from 0 to 255 inclusive')

        self._send_command('04 4D 00 00 ' + f'{brightness:02x}')
    
    def increase_brightness(self):
        self._send_command('04 0D 02')

    def decrease_brightness(self):
        self._send_command('04 0D 03')

    # exposure compensation

    def backlight(self, mode: bool):
        """Sets the backlight compensation mode of the camera
        :param mode: True for on, False for off
        """
        if mode:
            self._send_command('04 33 02')
        else:
            self._send_command('04 33 03')

    def set_aperture(self, aperture: int):
        """Sets the aperture of the camera
        :param aperture: 0-255
        """
        if not isinstance(aperture, int) or aperture < 0 or aperture > 255:
            raise ValueError('The aperture must be an integer from 0 to 255 inclusive')

        self._send_command('04 42 00 00 ' + f'{aperture:02x}')

    def increase_aperture(self):
        self._send_command('04 02 02')
    
    def decrease_aperture(self):
        self._send_command('04 02 03')
    
    def reset_aperture(self):
        self._send_command('04 02 00')

    def flip_horizontal(self, flip_mode: bool):
        """Sets the horizontal flip mode of the camera
        :param value: True for horizontal flip mode, False for normal mode
        """
        if flip_mode:
            self._send_command('04 61 02')
        else:
            self._send_command('04 61 03')

    def flip_vertical(self, flip_mode: bool):
        """Sets the vertical flip (mount) mode of the camera
        :param flip_mode: True for vertical flip mode, False for normal mode
        """
        if flip_mode:
            self._send_command('04 66 02')
        else:
            self._send_command('04 66 03')

    def flip(self, horizontal: bool, vertical: bool):
        """Sets the horizontal and vertical flip modes of the camera
        :param horizontal: True for horizontal flip mode, False for normal mode
        :param vertical: True for vertical flip mode, False for normal mode
        """
        if horizontal and vertical:
            self._send_command('04 A4 03')
        elif vertical:
            self._send_command('04 A4 02')
        elif horizontal:
            self._send_command('04 A4 01')
        else:
            self._send_command('04 A4 00')

    # noise reduction 2d

    # noise reduction 3d

    def defog(self, mode: bool):
        """Sets the defog mode of the camera, not supported on all cameras
        :param value: True for defog mode, False for normal mode
        """
        if mode:
            self._send_command('04 37 02 00')
        else:
            self._send_command('04 37 03 00')

    def save_preset(self, preset_num: int):
        """Saves many of the camera's settings in one of 16 slots (some cameras even have as many as 255 slots)"""
        if not 0 <= preset_num <= 255:
            raise ValueError('Preset number must be 0-255 inclusive')
        self._send_command(f'04 3F 01 {preset_num:02x}')

    def recall_preset(self, preset_num: int):
        """Instructs the camera to recall one of the 255 saved presets"""
        if not 0 <= preset_num <= 255:
            raise ValueError('Preset number must be 0-255 inclusive')
        self._send_command(f'04 3F 02 {preset_num:02x}')

    @staticmethod
    def _zero_padded_bytes_to_int(zero_padded: bytes, signed=True) -> int:
        """:param zero_padded: bytes like this: 0x01020304
        :param signed: is this a signed integer?
        :return: an integer like this 0x1234
        """
        unpadded_bytes = bytes.fromhex(zero_padded.hex()[1::2])
        return int.from_bytes(unpadded_bytes, 'big', signed=signed)

    def get_pantilt_position(self) -> Tuple[int, int]:
        """:return: two signed integers representing the absolute pan and tilt positions respectively"""
        response = self._send_command('06 12', query=True)
        pan_bytes = response[2:6]
        tilt_bytes = response[6:10]
        return self._zero_padded_bytes_to_int(pan_bytes), self._zero_padded_bytes_to_int(tilt_bytes)

    def get_zoom_position(self) -> int:
        """:return: an unsigned integer representing the absolute zoom position"""
        response = self._send_command('04 47', query=True)
        return self._zero_padded_bytes_to_int(response[1:], signed=False)

    def get_focus_mode(self) -> str:
        """:return: either 'auto' or 'manual'
        :raises ViscaException: if the response is not 2 or 3
        """
        modes = {2: 'auto', 3: 'manual'}
        response = self._send_command('04 38', query=True)
        try:
            mode = modes[response[-1]]
        except KeyError:
            mode = 'unknown'
            raise ViscaException(response)
        return mode

    # other inquiry commands