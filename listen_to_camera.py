import socket
import binascii

#camera_ip = '192.168.0.100'
camera_port = 52381
buffer_size = 1024

s.bind(('', camera_port))

visca_response_dictionary = {
    
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
    print(data)
    try:
        print(sequence_number, visca_response_dictionary[message_type])
    except:
        print(sequence_number, payload)