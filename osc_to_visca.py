# receive OSC messages and send VISCA controls to camera (both UDP)

# pip3 install oscpy
# https://github.com/kivy/oscpy
from oscpy.server import OSCThreadServer 
from time import sleep 
import socket
import binascii  # for printing the messages we send, not really necessary

# OSC receiver


# VISCA sender (socket)
ip = '192.168.0.100'
#ip = '127.0.0.1'
port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP

# VISCA Commands
sequence_number = 1 # a global variable that we'll iterate each command, remember 0x0001
reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')

def send_message(message_string):
    global sequence_number
    payload_type = bytearray.fromhex('01 00')
    payload = bytearray.fromhex(message_string)
    payload_length = len(payload).to_bytes(2, 'big')
    message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
    #s.sendto(reset_sequence_number_message,(ip, port))
    s.sendto(message, (ip, port))
    print(binascii.hexlify(message), ip, port, sequence_number)
    sequence_number += 1
    return message

def reset_sequence_number():
    reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
    s.sendto(reset_sequence_number_message,(ip, port))
    sequence_number = 1
    return sequence_number

#reset_sequence_number()




''' not working
osc = OSCThreadServer()  # See sources for all the arguments

def callback(*values):
    print("got values: {}".format(values))
    print('from', osc.get_sender)

osc_server = osc.listen(address='0.0.0.0', port=8000, default=True)
osc.bind(b'/address', callback)
print('osc bound')

sleep(10)
print('sleep done, exiting')
osc.stop()  # Stop the default socket
print('osc stopped')
osc.stop_all()  # Stop all sockets

# Here the server is still alive, one might call osc.listen() again

osc.terminate_server()  # Request the handler thread to stop looping

osc.join_server()  # Wait for the handler thread to finish pending tasks and exit
'''



''' working:
from oscpy.client import OSCClient

address = "10.0.0.30"
port = 9000

osc = OSCClient(address, port)
for i in range(10):
    osc.send_message(b'/1/fader1', [i])
    sleep(0.5)
    print('sent', i)
'''