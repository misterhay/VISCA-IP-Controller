# receive OSC messages and send VISCA controls to camera (both UDP)

# pip3 install aiosc
# https://pypi.org/project/aiosc/
# https://github.com/artfwo/aiosc
import asyncio
import aiosc
from math import floor
import socket
import binascii  # for printing the messages we send, not really necessary

# VISCA sender (socket)
camera_ip = '192.168.0.100'
#ip = '127.0.0.1'
camera_port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP


# VISCA Commands
sequence_number = 1 # a global variable that we'll iterate each command, remember 0x0001


camera_on = '81 01 04 00 02 FF'

def reset_sequence_number():
    reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
    s.sendto(reset_sequence_number_message,(camera_ip, camera_port))
    sequence_number = 1
    return sequence_number

reset_sequence_number()

def send_message(message_string):
    global sequence_number
    payload_type = bytearray.fromhex('01 00')
    payload = bytearray.fromhex(message_string)
    payload_length = len(payload).to_bytes(2, 'big')
    visca_message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
    s.sendto(visca_message, (camera_ip, camera_port))
    print(binascii.hexlify(visca_message), camera_ip, camera_port, sequence_number)
    sequence_number += 1
    return visca_message


# OSC sender
touchOSC_ip = '10.0.0.32'
touchOSC_port = 9000

def sendOSC(osc_command, osc_argument):
    print('this is not working...')
    #print(pan_speed)
    #send_loop = asyncio.get_event_loop()
    #send_loop.run_until_complete(aiosc.send((touchOSC_ip, touchOSC_port), '/1/'+osc_command, osc_argument))

# OSC receiving server

def parse_osc_message(osc_address, osc_path, args):
    global touchOSC_ip
    touchOSC_ip = osc_address[0]
    osc_path_list = osc_path.split('/')
    osc_command = osc_path_list[2]
    osc_argument = args[0]
    if osc_command == 'camera_on':
        if osc_argument > 0:
            #print(osc_command)
            send_message(camera_on)
    if osc_command == 'pan_tilt_speed':
        global pan_speed
        pan_speed = floor(osc_argument)
        sendOSC('pan_tilt_speed_label', pan_speed)


def protocol_factory():
    osc = aiosc.OSCProtocol({'//*': lambda osc_address, osc_path, *args: parse_osc_message(osc_address, osc_path, args)})
    return osc
receive_loop = asyncio.get_event_loop()
coro = receive_loop.create_datagram_endpoint(protocol_factory, local_addr=('0.0.0.0', 8000))
transport, protocol = receive_loop.run_until_complete(coro)
receive_loop.run_forever()



