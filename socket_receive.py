import socket

port = 52381
buffer_size = 1024
'''
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_socket.bind(('', port))

while True:
    data = receive_socket.recvfrom(buffer_size)
    print(data)
'''


# import thread module 
from _thread import *
import threading 

print_lock = threading.Lock() 

# thread function 
def threaded(s):
    while True:
        data = s.recvfrom(buffer_size)
        if not data:
            print('Bye')
            print_lock.release()
            break
        print(data)
    print('closing')
    s.close()

def Main():
    host = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    while True:
        data = s.recvfrom(buffer_size)
        print_lock.acquire()
        print('Connected')
        start_new_thread(threaded, (s,))
    s.close()


if __name__ == '__main__': 
	Main() 
