# receive OSC messages and send VISCA controls to camera (both UDP)

# pip3 install aiosc
# https://pypi.org/project/aiosc/
# https://github.com/artfwo/aiosc
import asyncio # for receiving OSC
import aiosc # for receiving OSC
# pip3 install python-osc
# https://pypi.org/project/python-osc/
from pythonosc import udp_client # for sending OSC
from math import floor  # for fader
import socket
import binascii  # for printing the messages we send

### VISCA sender (socket)
camera_ip = '192.168.0.100'
#camera_ip = '127.0.0.1'
camera_port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP

### VISCA receiver
buffer_size = 1024
s.bind(('', camera_port+1)) # use the port one higher than the camera's port
s.settimeout(2.0) # only wait for a response for 2 seconds

### VISCA Commands (Payloads)
camera_on = '81 01 04 00 02 FF'
information_display_off = '81 01 7E 01 18 03 FF'
memory_recall = '81 01 04 3F 02 0p FF' # p: Memory number (=0 to F)
memory_set = '81 01 04 3F 01 0p FF' # p: Memory number (=0 to F)
movement_speed = '01'
'''
pan_speed = '05'
tilt_speed = '05'
pan_up = '81 01 06 01 VV WW 03 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down = '81 01 06 01 VV WW 03 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_left = '81 01 06 01 VV WW 01 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_right = '81 01 06 01 VV WW 02 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_left = '81 01 06 01 VV WW 01 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_right = '81 01 06 01 VV WW 02 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_left = '81 01 06 01 VV WW 01 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_right = '81 01 06 01 VV WW 02 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_stop = '81 01 06 01 VV WW 03 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
'''
pan_dictionary = {
    'pan_up' : '81 01 06 01 VV WW 03 01 FF',
    'pan_down' : '81 01 06 01 VV WW 03 02 FF',
    'pan_left' : '81 01 06 01 VV WW 01 03 FF',
    'pan_right' : '81 01 06 01 VV WW 02 03 FF',
    'pan_up_left' : '81 01 06 01 VV WW 01 01 FF',
    'pan_up_right' : '81 01 06 01 VV WW 02 01 FF',
    'pan_down_left' : '81 01 06 01 VV WW 01 02 FF',
    'pan_down_right' : '81 01 06 01 VV WW 02 02 FF'}

pan_stop = '81 01 06 01 15 15 03 03 FF' # replaced VV and WW with 15
pan_home = '81 01 06 04 FF'
pan_reset = '81 01 06 05 FF'
focus_stop = '81 01 04 08 00 FF'
focus_far = '81 01 04 08 02 FF'
focus_near = '81 01 04 08 03 FF'
focus_far_variable = '81 01 04 08 2p FF'.replace('p', '7') # 0 low to 7 high
focus_near_variable = '81 01 04 08 3p FF'.replace('p', '7') # 0 low to 7 high
focus_direct = '81 01 04 48 0p 0q 0r 0s FF' #.replace('p', ) q, r, s
focus_auto = '81 01 04 38 02 FF'
focus_manual = '81 01 04 38 03 FF'
focus_infinity = '81 01 04 18 02 FF'
zoom_stop = '81 01 04 07 00 FF'
zoom_tele = '81 01 04 07 02 FF'
zoom_wide = '81 01 04 07 03 FF'
zoom_tele_variable = '81 01 04 07 2p FF' # p=0 (Low) to 7 (High)
zoom_wide_variable = '81 01 04 07 3p FF' # p=0 (Low) to 7 (High)
zoom_direct = '81 01 04 47 0p 0q 0r 0s FF' # pqrs: Zoom Position

def reset_sequence_number_function():  # this should probably be rolled into the send_visca function
    reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
    s.sendto(reset_sequence_number_message,(camera_ip, camera_port))
    global sequence_number
    sequence_number = 1
    print('Reset sequence number to', sequence_number)
    try:
        data = s.recvfrom(buffer_size)
        received_message = binascii.hexlify(data[0])
        #print('Received', received_message)
        data = s.recvfrom(buffer_size)
        received_message = binascii.hexlify(data[0])
        #print('Received', received_message)
        send_osc('reset_sequence_number', 1.0)
    except socket.timeout: # s.settimeout(2.0) #above
        received_message = 'No response from camera'
        print(received_message)
        send_osc('reset_sequence_number', 0.0)
    return sequence_number

def send_visca(message_string):
    global sequence_number
    payload_type = bytearray.fromhex('01 00')
    payload = bytearray.fromhex(message_string)
    payload_length = len(payload).to_bytes(2, 'big')
    visca_message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
    s.sendto(visca_message, (camera_ip, camera_port))
    print(binascii.hexlify(visca_message), 'sent to', camera_ip, camera_port, sequence_number)
    sequence_number += 1
    # wait for acknowledge and completion messages
    try:
        data = s.recvfrom(buffer_size)
        received_message = binascii.hexlify(data[0])
        #print('Received', received_message)
        data = s.recvfrom(buffer_size)
        received_message = binascii.hexlify(data[0])
        if received_message == b'9051ff':
            print('Received okay')
        else:
            print('Error')
        #print('Received', received_message)
    except socket.timeout: # s.settimeout(2.0) #from above
        received_message = 'No response from camera'
        print(received_message)
        send_osc('reset_sequence_number', 0.0)
    #return visca_message
    return received_message

### OSC server and client
osc_receive_port = 8000
touchOSC_ip = '10.0.0.32' # there must be a way to listen for this... maybe osc_address[0]
osc_send_port = 9000

def send_osc(osc_command, osc_send_argument):
    osc_message_to_send = '/1/' + osc_command
    osc_client = udp_client.SimpleUDPClient(touchOSC_ip, osc_send_port)
    osc_client.send_message(osc_message_to_send, osc_send_argument)

### OSC receiving server

def parse_osc_message(osc_address, osc_path, args):
    global touchOSC_ip
    touchOSC_ip = osc_address[0]
    osc_path_list = osc_path.split('/')
    osc_command = osc_path_list[2]
    osc_argument = args[0]
    if osc_command == 'camera_on':
        send_visca(camera_on)
    elif osc_command == 'reset_sequence_number':
        reset_sequence_number_function()
    elif 'memory_' in osc_command:
        memory_preset_number = osc_command[-1]
        if osc_argument > 0:
            if 'recall' in osc_command:
                print('Memory recall', memory_preset_number)
                send_visca(information_display_off) # so that it doesn't display on-screen
                send_visca(memory_recall.replace('p', memory_preset_number))
            elif 'set' in osc_command:
                print('Memory set', memory_preset_number)
                send_visca(memory_set.replace('p', memory_preset_number))
    elif 'zoom' in osc_command:
        if osc_argument > 0:
            if osc_command == 'zoom_tele':
                send_visca(zoom_tele)
            elif osc_command == 'zoom_wide':
                send_visca(zoom_wide)
        else: # when the button is released the osc_argument should be 0
            send_visca(zoom_stop)
    elif 'focus' in osc_command:
        if osc_command == 'focus_auto':
            send_visca(focus_auto)
        if osc_argument > 0:
            if osc_command == 'focus_far':
                send_visca(focus_far)
            elif osc_command == 'focus_near':
                send_visca(focus_near)
        else: # when the button is released the osc_argument should be 0
            send_visca(focus_stop)
    elif 'speed' in osc_command: # e.g. speed01 or speed15, from buttons not a slider
        global movement_speed
        movement_speed = osc_command[5:]
        send_osc('MovementSpeedLabel', movement_speed)
        #send_osc(osc_command, 1)
        print('set speed to', movement_speed)
    elif 'pan' in osc_command:
        if 'speed' not in osc_command:  # this is a relic of the old TouchOSC layout
            if osc_argument > 0:
                pan_command = pan_dictionary[osc_command].replace('VV', movement_speed).replace('WW', movement_speed)
                send_visca(pan_command)
            else: # when the button is released the osc_argument should be 0
                send_visca(pan_stop)
        #else:
        #    print("I can't yet set pan_tilt_speed")
    else:
        print("I don't know what to do with", osc_command, osc_argument)
    send_osc('SentMessageLabel', osc_command)


## Start off by resetting sequence number
sequence_number = 1 # a global variable that we'll iterate each command, remember 0x0001
reset_sequence_number_function()

## Then start the OSC server to receive messages
def protocol_factory():
    osc = aiosc.OSCProtocol({'//*': lambda osc_address, osc_path, *args: parse_osc_message(osc_address, osc_path, args)})
    return osc
receive_loop = asyncio.get_event_loop()
coro = receive_loop.create_datagram_endpoint(protocol_factory, local_addr=('0.0.0.0', osc_receive_port))
transport, protocol = receive_loop.run_until_complete(coro)
receive_loop.run_forever()