import socket

socket_ip = '127.0.0.1'
socket_port = 52381

sending_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP

camera_on = '81 01 04 00 02 FF'
sequence_number = 1
payload_type = bytearray.fromhex('01 00')
payload = bytearray.fromhex(camera_on)
payload_length = len(payload).to_bytes(2, 'big')
visca_message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload

sending_socket.sendto(visca_message, (socket_ip, socket_port))
print('Sent', camera_on, 'to', socket_ip)