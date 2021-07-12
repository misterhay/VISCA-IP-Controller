

def Receiver(port):
    import socket
    import binascii
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))

    buffer_size = 1024

    visca_response_dictionary = {
        b'01':'sequence number reset',
        b'0f01':'sequence number error',
        b'9041ff':'acknowledge',
        b'9051ff':'complete',
    }

    while True:
        data = s.recvfrom(buffer_size)
        message = data[0]
        address_port = data[1]
        address = address_port[0]
        port = address_port[1]
        payload_type = message[0:2]
        payload_length = int(binascii.hexlify(message[2:4]), 16)
        sequence_number = int(binascii.hexlify(message[4:8]), 16)
        payload = binascii.hexlify(message[8:])
        message_type = payload[0:8]
        print(data)
        print('sequence_number', sequence_number)
        print('address', address)
        print('payload_type', payload_type)
        print('payload', payload)
        try:
            print(sequence_number, visca_response_dictionary[message_type])
        except:
            print(sequence_number, payload)