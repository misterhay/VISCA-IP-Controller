# https://pro.sony/s3/2019/01/16020225/AES6100121.pdf
# https://gitlab.viarezo.fr/2018corona/viscaoverip/blob/master/camera2.py

import socket
import binascii # for printing the messages we send, not really necessary

#camera_ip = '192.168.0.100'
camera_ip = '127.0.0.1'
camera_port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
# for receiving
buffer_size = 1024
s.bind(('', camera_port+1)) # use the port one higher than the camera's port
s.settimeout(2.0) # only wait for a response for 2 seconds


# Payloads

sequence_number = 1 # a global variable that we'll iterate each command, remember 0x0001
reset_sequence_number = '02 00 00 01 00 00 00 01 01'

camera_on = '81 01 04 00 02 FF'
camera_off = '81 01 04 00 03 FF'

information_display_on = '81 01 7E 01 18 02 FF'
information_display_off = '81 01 7E 01 18 03 FF'

zoom_stop = '81 01 04 07 00 FF'
zoom_tele = '81 01 04 07 02 FF'
zoom_wide = '81 01 04 07 03 FF'
zoom_tele_variable = '81 01 04 07 2p FF' # p=0 (Low) to 7 (High)
zoom_wide_variable = '81 01 04 07 3p FF' # p=0 (Low) to 7 (High)
zoom_direct = '81 01 04 47 0p 0q 0r 0s FF' # pqrs: Zoom Position

memory_reset = '81 01 04 3F 00 0p FF'
memory_set = '81 01 04 3F 01 0p FF' # p: Memory number (=0 to F)
memory_recall = '81 01 04 3F 02 0p FF' # p: Memory number (=0 to F)

#Pan-tilt Drive
# VV: Pan speed setting 0x01 (low speed) to 0x18
# WW: Tilt speed setting 0x01 (low speed) to 0x17
pan_speed = '05'
tilt_speed = '05'
speed = 5
# YYYY: Pan Position DE00 to 2200 (CENTER 0000)
# ZZZZ: Tilt Position FC00 to 1200 (CENTER 0000)
YYYY = '0000'
ZZZZ = '0000'

pan_up = '81 01 06 01 VV WW 03 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down = '81 01 06 01 VV WW 03 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_left = '81 01 06 01 VV WW 01 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_right = '81 01 06 01 VV WW 02 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_left = '81 01 06 01 VV WW 01 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_up_right = '81 01 06 01 VV WW 02 01 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_left = '81 01 06 01 VV WW 01 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_down_right = '81 01 06 01 VV WW 02 02 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
pan_stop = '81 01 06 01 VV WW 03 03 FF'.replace('VV', str(pan_speed)).replace('WW', str(tilt_speed))
#pan_absolute_position = '81 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV)) #YYYY[0]
#pan_relative_position = '81 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF'.replace('VV', str(VV))
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

def memory_recall_function(memory_number):
    message_string = memory_recall.replace('p', str(memory_number))
    send_message(information_display_off) # otherwise we see a message on the camera output
    message = send_message(message_string)
    return message

def memory_set_function(memory_number):
    message_string = memory_set.replace('p', str(memory_number))
    message = send_message(message_string)
    return message

def send_message(message_string):
    global sequence_number
    global received_message
    payload_type = bytearray.fromhex('01 00')
    payload = bytearray.fromhex(message_string)
    payload_length = len(payload).to_bytes(2, 'big')
    message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
    if message_string == reset_sequence_number:
        sequence_number = 1
    else:
        sequence_number += 1
    s.sendto(message, (camera_ip, camera_port))
    print(binascii.hexlify(message), 'sent to', camera_ip, camera_port, sequence_number)
    # add a timeout in case we don't hear back
    try:
        data = s.recvfrom(buffer_size)
        received_message = binascii.hexlify(data[0])
        print('Received', received_message)
        data = s.recvfrom(buffer_size)
        received_message = binascii.hexlify(data[0])
        print('Received', received_message)
    except socket.timeout: # s.settimeout(2.0) #above
        received_message = 'No response from camera'
        print(received_message)

    if received_message == b'9051ff':
        display_message.set('Connected')
    else:
        display_message.set(received_message)
    return received_message

def reset_sequence_number_function(): # we don't really need this anymore
    reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
    s.sendto(reset_sequence_number_message,(camera_ip, camera_port))
    sequence_number = 1
    return sequence_number

def store_network_values(ip_value, port_value): # we don't really need this anymore
    global camera_ip
    global camera_port
    camera_ip = ip_value
    camera_port = port_value
    print(camera_ip, camera_port)
    return camera_ip, camera_port

# GUI
from tkinter import *
root = Tk()
display_message = StringVar()
root.title('VISCA IP Camera Controller')
Label(root, text='VISCA IP Camera Controller').grid(row=0, column=0, columnspan=100)

Button(root, text='Connect', command=lambda: send_message(reset_sequence_number)).grid(row=1, column=6)
Button(root, text='Cam On', command=lambda: send_message(camera_on)).grid(row=2, column=6)

Label(root, text='Presets').grid(row=1, column=0, columnspan=2)
Button(root, text=1, command=lambda: memory_recall_function(0)).grid(row=2, column=0)
Button(root, text=2, command=lambda: memory_recall_function(1)).grid(row=2, column=1, padx=5)
Button(root, text=3, command=lambda: memory_recall_function(2)).grid(row=3, column=0)
Button(root, text=4, command=lambda: memory_recall_function(3)).grid(row=3, column=1)
Button(root, text=5, command=lambda: memory_recall_function(4)).grid(row=4, column=0)
Button(root, text=6, command=lambda: memory_recall_function(5)).grid(row=4, column=1)

Button(root, text='↑', command=lambda: send_message(pan_up)).grid(row=1, column=3)
Button(root, text='←', command=lambda: send_message(pan_left)).grid(row=2, column=2)
Button(root, text='→', command=lambda: send_message(pan_right)).grid(row=2, column=4)
Button(root, text='↓', command=lambda: send_message(pan_down)).grid(row=3, column=3)
Button(root, text='↖', command=lambda: send_message(pan_up_left)).grid(row=1, column=2)
Button(root, text='↗', command=lambda: send_message(pan_up_right)).grid(row=1, column=4)
Button(root, text='↙', command=lambda: send_message(pan_down_left)).grid(row=3, column=2)
Button(root, text='↘', command=lambda: send_message(pan_down_right)).grid(row=3, column=4)
Button(root, text='Stop', command=lambda: send_message(pan_stop)).grid(row=2, column=3)
Button(root, text='Home', command=lambda: send_message(pan_home)).grid(row=4, column=3)

# slider to set speed for pan_speed and tilt_speed (0x01 to 0x17)
Scale(root, from_=0, to=17, variable=speed, orient=HORIZONTAL, label='Speed').grid(row=5, column=2, columnspan=3)

Button(root, text='Zoom In', command=lambda: send_message(zoom_tele)).grid(row=1, column=5)
Button(root, text='Zoom Stop', command=lambda: send_message(zoom_stop)).grid(row=2, column=5)
Button(root, text='Zoom Out', command=lambda: send_message(zoom_wide)).grid(row=3, column=5)

Button(root, text='Focus Near', command=lambda: send_message(focus_near)).grid(row=4, column=5)
Button(root, text='Focus Far', command=lambda: send_message(focus_far)).grid(row=5, column=5)

Button(root, text='Info Off', command=lambda: send_message(information_display_off)).grid(row=5, column=6)

# IP Label
Label(root, text=camera_ip+':'+str(camera_port)).grid(row=6, column=0, columnspan=3)
# Connection Label
Label(root, textvariable=display_message).grid(row=6, column=4, columnspan=3)

root.mainloop()