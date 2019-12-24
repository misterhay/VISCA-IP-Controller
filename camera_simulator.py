import socket
from time import sleep
import binascii

port = 52381
buffer_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))

acknowledge_message = bytearray.fromhex('90 4Y FF'.replace('Y', '1')) # 1 = socket number
completion_message = bytearray.fromhex('90 5Y FF'.replace('Y', '1'))

while True:
    data = s.recvfrom(buffer_size)
    message = data[0]
    address_port = data[1]
    print(address_port, 'sent', binascii.hexlify(message))
    s.sendto(acknowledge_message, address_port)
    sleep(0.1)
    s.sendto(completion_message, address_port)