import socket
from time import sleep
import binascii

port = 52381
buffer_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))

acknowledge_message = bytearray.fromhex('90 4Y FF'.replace('Y', '1')) # 1 = socket number
completion_message = bytearray.fromhex('90 5Y FF'.replace('Y', '1'))

visca_command_dictionary = {
    b'81010601':'pan',
    b'81010408':'focus',
    b'81010438':'autofocus',
    b'81010407':'zoom',
    b'8101043f':'memory',
    b'81017e01':'information_display',
    b'81010400':'camera_power',
    b'01':'reset_sequence_number'
    }


while True:
    data = s.recvfrom(buffer_size)
    message = data[0]
    address_port = data[1]
    payload_type = message[0:2]
    payload_length = int(binascii.hexlify(message[2:4]), 16)
    sequence_number = int(binascii.hexlify(message[4:8]), 16)
    payload = binascii.hexlify(message[8:])
    message_type = payload[0:8]
    try:
        print(sequence_number, visca_command_dictionary[message_type])
    except:
        print(sequence_number, payload)
    s.sendto(acknowledge_message, address_port)
    sleep(0.1)
    s.sendto(completion_message, address_port)