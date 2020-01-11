import socket

camera_ip = '192.168.0.100'
#camera_ip = '127.0.0.1'
camera_port = 52381
buffer_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP

# only necessary for receiving, we can probably bind to camera_ip
#s.bind(('', camera_port)) # use the port one higher than the camera's port

'''
camera_on = '81 01 04 00 02 FF'
sequence_number = 1
payload_type = bytearray.fromhex('01 00')
payload = bytearray.fromhex(camera_on)
payload_length = len(payload).to_bytes(2, 'big')
visca_message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
'''
visca_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')

s.sendto(visca_message, (camera_ip, camera_port))
print('Sent', visca_message, 'to', camera_ip)

# listen for a response
'''
import binascii
print('listening')
data = s.recvfrom(buffer_size)
received_message = binascii.hexlify(data[0])
print('Received', received_message)
'''
#data = s.recvfrom(buffer_size)
#received_message = binascii.hexlify(data[0])
#print('Received', received_message)
