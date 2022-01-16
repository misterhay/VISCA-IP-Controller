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
    def __init__(self, ip, port=52381):
        """:param ip: the IP address or hostname of the camera you want to talk to.
        :param port: the port number to use.
        """
        self._location = (ip, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # for UDP stuff
        self._sock.bind(('', port))
        self._sock.settimeout(0.1)

        self.num_missed_responses = 0
        self.sequence_number = 0  # This number is encoded in each message and incremented after sending each message
        self.num_retries = 5
        self.reset_sequence_number()
        self._send_command('00 01')  # clear the camera's interface socket

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
        payload_length = len(preamble + payload_bytes + terminator).to_bytes(2, 'big')


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
        :raises ViscaException: if the response if an error and not an acknowledge or completion
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

    def pantilt(self, pan_speed: int, tilt_speed: int, pan_position=None, tilt_position=None, relative=False):
        """Commands the camera to pan and/or tilt.
        You must specify both pan_position and tilt_position OR specify neither

        :param pan_speed: -24 to 24 where negative numbers cause a left pan and 0 causes panning to stop
        :param tilt_speed: -24 to 24 where negative numbers cause a downward tilt and 0 causes tilting to stop
        :param pan_position: if specified, the camera will move this distance or go to this absolute position
            depending on the value of `relative`.
            Valid values are integers by default between 0x2200 and 0xDE00.
            Camera users may set more restrictive pan limits for a camera.
        :param tilt_position: if specified, the camera will move this distance or go to this absolute position
            depending on the value of `relative`.
            Valid values are integers 0x1200 to 0xFC00 if image flip is on or 0xEE00 to 0x400 if image flip is off.
            Camera users may set more restrictive tilt limits for a camera
        :param relative: If set to True, the position will be relative instead of absolute (default).

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
            raise ValueError('All parameters must be ints or None')

        pan_speed_hex = f'{abs(pan_speed):02x}'
        tilt_speed_hex = f'{abs(tilt_speed):02x}'

        if None not in position_params:
            pan_position_hex = ' '.join(['0' + char for char in f'{pan_position:04x}'])
            tilt_position_hex = ' '.join(['0' + char for char in f'{tilt_position:04x}'])
            relative_hex = '03' if relative else '02'
            self._send_command(
                '06' + relative_hex + pan_speed_hex + tilt_speed_hex + pan_position_hex + tilt_position_hex
            )

        else:
            payload_start = '06 01'

            def get_direction_hex(speed: int):
                if speed > 0:
                    return '01'
                if speed < 0:
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
        :param speed: -7 to 7 where positive numbers zoom in and zero stops the zooming
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

    def get_focus_mode(self) -> str:
        """:return: either 'auto' or 'manual'"""
        modes = {2: 'auto', 3: 'manual'}

        response = self._send_command('04 38', query=True)
        return modes[response[-1]]

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
            direction_hex = '2'
        else:
            direction_hex = '3'

        self._send_command(f'04 08 {direction_hex}{speed_hex}')

    def save_preset(self, preset_num: int):
        """Saves many of the camera's settings in one of 16 slots"""
        if not 0 <= preset_num <= 15:
            raise ValueError('Preset num must be 0-15 inclusive')

        self._send_command(f'04 3F 01 0{preset_num:x}')

    def recall_preset(self, preset_num: int):
        """Instructs the camera to recall one of the 16 saved presets"""
        if not 0 <= preset_num <= 16:
            raise ValueError('Preset num must be 0-15 inclusive')

        self._send_command(f'04 3F 02 0{preset_num:x}')

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
        pan_bytes = response[1:5]
        tilt_bytes = response[5:9]

        return self._zero_padded_bytes_to_int(pan_bytes), self._zero_padded_bytes_to_int(tilt_bytes)

    def get_zoom_position(self) -> int:
        """:return: an unsigned integer representing the absolute zoom position"""
        response = self._send_command('04 47', query=True)
        return self._zero_padded_bytes_to_int(response[1:], signed=False)
