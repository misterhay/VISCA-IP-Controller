import socket
from typing import Optional

from visca_over_ip.message import Message
from visca_over_ip.exceptions import ViscaException, NoQueryResponse

SEQUENCE_NUM_MAX = 2 ** 32 - 1


class Connection:
    """Represents a connection to a single camera.
    Cannot be used to control multiple cameras.
    """
    def __init__(self, ip: str, port=52381):
        """:param ip: the IP address or hostname of the camera you want to talk to.
        :param port: the port number to use. 52381 is the default for most cameras.
        """
        self._location = (ip, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # for UDP stuff
        self._sock.bind(('', port))
        self._sock.settimeout(0.1)  # TODO

        self.sequence_number = 0
        self.reset_sequence_number()
        self.send(Message('00 01'))  # clear the camera's interface socket

    def send(self, message: Message):
        """sends the given message, retransmitting if necessary"""
        exception = None

        for retry_num in range(5):
            self._increment_sequence_number()

            self._sock.sendto(
                message.render_to_bytes(self.sequence_number),
                self._location
            )

            try:
                response = self._receive_response()
            except ViscaException as exc:
                exception = exc
            else:
                if response is not None:
                    return response[1:-1]
                elif not message.is_query:
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
                break

    def _increment_sequence_number(self):
        self.sequence_number += 1
        if self.sequence_number > SEQUENCE_NUM_MAX:
            self.sequence_number = 0

    def reset_sequence_number(self):
        self.sequence_number = 0
        self.send(Message(message_start_hex='02 00', payload_start_hex='', payload_hex='01', payload_end_hex=''))

    def close(self):
        """Only one camera can be bound to a socket at once.
        If you want to connect to another camera which uses the same communication port,
        first call this method on the first connection
        """
        self._sock.close()
