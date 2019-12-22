# receive OSC messages and send VISCA controls to camera (both UDP)

# pip3 install aiosc
# https://pypi.org/project/aiosc/
# https://github.com/artfwo/aiosc
import asyncio
import aiosc
from math import floor  # for fader
import socket
import binascii  # for printing the messages we send

### VISCA sender (socket)
camera_ip = '192.168.0.100'
camera_port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP


### VISCA Commands (Payloads)
camera_on = '81 01 04 00 02 FF'
information_display_off = '81 01 7E 01 18 03 FF'
memory_recall = '81 01 04 3F 02 0p FF' # p: Memory number (=0 to F)
memory_set = '81 01 04 3F 01 0p FF' # p: Memory number (=0 to F)
pan_up = '81 01 06 01 VV WW 03 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down = '81 01 06 01 VV WW 03 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_left = '81 01 06 01 VV WW 01 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_right = '81 01 06 01 VV WW 02 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_left = '81 01 06 01 VV WW 01 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_right = '81 01 06 01 VV WW 02 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_left = '81 01 06 01 VV WW 01 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_right = '81 01 06 01 VV WW 02 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_stop = '81 01 06 01 VV WW 03 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
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

def reset_sequence_number():
    reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
    s.sendto(reset_sequence_number_message,(camera_ip, camera_port))
    sequence_number = 1
    return sequence_number

## Start off by resetting sequence number
reset_sequence_number()
sequence_number = 1 # a global variable that we'll iterate each command, remember 0x0001

def send_visca(message_string):
    global sequence_number
    payload_type = bytearray.fromhex('01 00')
    payload = bytearray.fromhex(message_string)
    payload_length = len(payload).to_bytes(2, 'big')
    visca_message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
    s.sendto(visca_message, (camera_ip, camera_port))
    print(binascii.hexlify(visca_message), camera_ip, camera_port, sequence_number)
    sequence_number += 1
    return visca_message


### OSC sender
touchOSC_ip = '10.0.0.32'
touchOSC_port = 9000

def sendOSC(osc_command, osc_argument):
    print('this is not working...')
    #print(pan_speed)
    #send_loop = asyncio.get_event_loop()
    #send_loop.run_until_complete(aiosc.send((touchOSC_ip, touchOSC_port), '/1/'+osc_command, osc_argument))

### OSC receiving server

#consider using eval() to run functions from osc_path statements
def parse_osc_message(osc_address, osc_path, args):
    global touchOSC_ip
    touchOSC_ip = osc_address[0]
    osc_path_list = osc_path.split('/')
    osc_command = osc_path_list[2]
    osc_argument = args[0]
    if osc_command == 'camera_on':
        if osc_argument > 0:
            send_visca(camera_on)
    elif 'memory_' in osc_command:
        memory_preset_number = osc_command[-1]
        if osc_argument > 0:
            if 'recall' in osc_command:
                send_visca(information_display_off)
                #wait for acknowledgement
                send_visca(memory_recall.replace('p', memory_preset_number))
    elif osc_command == 'pan_tilt_speed':
        global pan_speed
        pan_speed = floor(osc_argument)
        sendOSC('pan_tilt_speed_label', pan_speed)
    else:
        print(osc_command, osc_argument)


def protocol_factory():
    osc = aiosc.OSCProtocol({'//*': lambda osc_address, osc_path, *args: parse_osc_message(osc_address, osc_path, args)})
    return osc
receive_loop = asyncio.get_event_loop()
coro = receive_loop.create_datagram_endpoint(protocol_factory, local_addr=('0.0.0.0', 8000))
transport, protocol = receive_loop.run_until_complete(coro)
receive_loop.run_forever()



