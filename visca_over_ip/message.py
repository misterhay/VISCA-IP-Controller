class Message:
    """Represents a VISCA over IP message.
    The intended use example:
    m = Message('04 38 02')  # auto focus
    connection.send(m)
    """
    def __init__(self, payload_hex: str, query=False,
                 message_start_hex='01 00', payload_start_hex='81', payload_end_hex='ff'):
        """:param payload_hex: the actual content of the message. For example "06 05" to reset pantilt
        :param query: if True, this message is a query type starting with 09 instead of 01
        :param message_start_hex: the first two bytes of the message before the payload or anything
        :param payload_start_hex: the first byte of the payload
        :param payload_end_hex: the last byte of the payload and the message
        """
        self.payload_hex = payload_hex
        self.is_query = query
        self.message_start_hex = message_start_hex
        self.payload_start_hex = payload_start_hex
        self.payload_end_hex = payload_end_hex

    def render_to_bytes(self, sequence_number: int) -> bytes:
        """:param sequence_number: a unique sequential ID for the message.
        This needs to be incremented if retransmitting a particular message.
        :return: bytes that can be sent to the camera
        """
        message_start_bytes = bytes.fromhex(self.message_start_hex)
        query_byte = b'\x09' if self.is_query else b'\x01'
        payload_bytes = bytes.fromhex(self.payload_start_hex + self.payload_hex + self.payload_end_hex)
        payload_length = len(payload_bytes).to_bytes(2, 'big')
        sequence_bytes = sequence_number.to_bytes(4, 'big')

        return message_start_bytes + query_byte + payload_length + sequence_bytes + payload_bytes
