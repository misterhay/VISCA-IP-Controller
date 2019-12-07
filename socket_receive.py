import socket

port = 52381
buffer_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.bind(('127.0.0.1', port))
s.bind(('', port))

while True:
    data = s.recvfrom(buffer_size)
    print(data)