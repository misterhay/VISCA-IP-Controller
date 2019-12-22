import socket

port = 52381
buffer_size = 1024

receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.bind(('127.0.0.1', port))
receive_socket.bind(('', port))

while True:
    data = receive_socket.recvfrom(buffer_size)
    print(data)