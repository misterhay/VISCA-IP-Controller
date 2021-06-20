#!/usr/bin/env python
# https://pro.sony/s3/2019/01/16020225/AES6100121.pdf
# https://gitlab.viarezo.fr/2018corona/viscaoverip/blob/master/camera2.py
# sudo apt install python3-tk

import socket
import binascii # for printing the messages we send, not really necessary
from time import sleep

camera_ip = '192.168.0.100'
#camera_ip = '127.0.0.1'
camera_port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
# for receiving
#buffer_size = 1024
#s.bind(('', camera_port)) # use the port one higher than the camera's port
#s.settimeout(1) # only wait for a response for 1 second


# Payloads
received_message = '' # a place to store the OSC messages we'll receive
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
movement_speed = '05'
pan_speed = movement_speed
tilt_speed = movement_speed

# YYYY: Pan Position DE00 to 2200 (CENTER 0000)
# ZZZZ: Tilt Position FC00 to 1200 (CENTER 0000)
#YYYY = '0000'
#ZZZZ = '0000'
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
zoom_direct = '81 01 04 47 0p 0q 0r 0s FF' # pqrs: Zoom Position
zoom_focus_direct = '81 01 04 47 0p 0q 0r 0s 0t 0u 0v 0w FF' # pqrs: Zoom Position  tuvw: Focus Position

inquiry_lens_control = '81 09 7E 7E 00 FF'
# response: 81 50 0p 0q 0r 0s 0H 0L 0t 0u 0v 0w 00 xx xx FF
inquiry_camera_control = '81 09 7E 7E 01 FF'

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
    send_message(information_display_off) # otherwise we see a message on the camera output
    sleep(0.25)
    message_string = memory_recall.replace('p', str(memory_number))
    message = send_message(message_string)
    sleep(1)
    send_message(information_display_off) # to make sure it doesn't display "done"
    return message

def memory_set_function(memory_number):
    hexadecimal_memory_number = hex(memory_number)[-1]
    message_string = memory_set.replace('p', hexadecimal_memory_number)
    #print(message_string)
    message = send_message(message_string)
    return message

def send_message(message_string):
    global sequence_number
    #global received_message
    payload_type = bytearray.fromhex('01 00')
    payload = bytearray.fromhex(message_string)
    payload_length = len(payload).to_bytes(2, 'big')
    message = payload_type + payload_length + sequence_number.to_bytes(4, 'big') + payload
    #if message_string == reset_sequence_number:
    #    sequence_number = 1
    #    #sequence_number = 4294967295
    #else:
    #    sequence_number += 1
    sequence_number += 1
    s.sendto(message, (camera_ip, camera_port))
    #print(binascii.hexlify(message), 'sent to', camera_ip, camera_port, sequence_number)
    # add a timeout in case we don't hear back
    '''
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

    #if received_message == b'01110003000000119051ff':
    if received_message[0:4] == '0111':
        display_message.set('Connected')
    else:
        display_message.set(received_message[0:4])
    #'''
    return received_message

#def pan(direction):
def pan():
    pan_speed = hex(pan_speed_slider.get())[2:]
    tilt_speed = hex(tilt_speed_slider.get())[2:]
    if len(pan_speed) == 1:
        pan_speed = '0'+pan_speed
    if len(tilt_speed) == 1:
        tilt_speed = '0'+tilt_speed
    print(len(pan_speed), pan_speed, len(tilt_speed), tilt_speed)

def save_preset_labels():
    with open('preset_labels.txt', 'w') as f:
        for entry in entry_boxes:
            f.write(entry.get())
            f.write('\n')
    f.close()

def reset_sequence_number_function():
    global sequence_number
    reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')
    s.sendto(reset_sequence_number_message,(camera_ip, camera_port))
    sequence_number = 1
    return sequence_number

# start by resetting the sequence number
reset_sequence_number_function()

# GUI

from tkinter import Tk, StringVar, Button, Label, Entry, Scale, W
root = Tk()
display_message = StringVar()
root.title('VISCA IP Camera Controller')
root['background'] = 'white'
#Label(root, text='VISCA IP Camera Controller').grid(row=0, column=0, columnspan=100)

store_column = 0
label_column = 1
recall_column = 2
pan_tilt_column = 5
pan_tilt_row = 1
zoom_column = 3
zoom_row = 4

focus_column = 3
focus_row = 8
on_off_column = 3
on_off_row = 11
button_width = 8
store_color = 'red'
recall_color = 'light grey'
pan_tilt_color = 'white'
zoom_color = 'light blue'
focus_color = 'cyan'
on_off_color = 'violet'

# Preset store buttons
Label(root, text='Store', bg=store_color).grid(row=1, column=store_column)
Button(root, text=0, width=3, bg=store_color, command=lambda: memory_set_function(0)).grid(row=2, column=store_column)
Button(root, text=1, width=3, bg=store_color, command=lambda: memory_set_function(1)).grid(row=3, column=store_column)
Button(root, text=2, width=3, bg=store_color, command=lambda: memory_set_function(2)).grid(row=4, column=store_column)
Button(root, text=3, width=3, bg=store_color, command=lambda: memory_set_function(3)).grid(row=5, column=store_column)
Button(root, text=4, width=3, bg=store_color, command=lambda: memory_set_function(4)).grid(row=6, column=store_column)
Button(root, text=5, width=3, bg=store_color, command=lambda: memory_set_function(5)).grid(row=7, column=store_column)
Button(root, text=6, width=3, bg=store_color, command=lambda: memory_set_function(6)).grid(row=8, column=store_column)
Button(root, text=7, width=3, bg=store_color, command=lambda: memory_set_function(7)).grid(row=9, column=store_column)
Button(root, text=8, width=3, bg=store_color, command=lambda: memory_set_function(8)).grid(row=10, column=store_column)
Button(root, text=9, width=3, bg=store_color, command=lambda: memory_set_function(9)).grid(row=11, column=store_column)
Button(root, text='A', width=3, bg=store_color, command=lambda: memory_set_function(10)).grid(row=12, column=store_column)
Button(root, text='B', width=3, bg=store_color, command=lambda: memory_set_function(11)).grid(row=13, column=store_column)
Button(root, text='C', width=3, bg=store_color, command=lambda: memory_set_function(12)).grid(row=14, column=store_column)
Button(root, text='D', width=3, bg=store_color, command=lambda: memory_set_function(13)).grid(row=15, column=store_column)
Button(root, text='E', width=3, bg=store_color, command=lambda: memory_set_function(14)).grid(row=16, column=store_column)
Button(root, text='F', width=3, bg=store_color, command=lambda: memory_set_function(15)).grid(row=17, column=store_column)

# Recall buttons and entries (as labels)
Label(root, text='Recall', bg=recall_color).grid(row=1, column=recall_column)
Button(root, text=0, width=5, bg=recall_color, command=lambda: memory_recall_function(0)).grid(row=2, column=recall_column)
Button(root, text=1, width=5, bg=recall_color, command=lambda: memory_recall_function(1)).grid(row=3, column=recall_column)
Button(root, text=2, width=5, bg=recall_color, command=lambda: memory_recall_function(2)).grid(row=4, column=recall_column)
Button(root, text=3, width=5, bg=recall_color, command=lambda: memory_recall_function(3)).grid(row=5, column=recall_column)
Button(root, text=4, width=5, bg=recall_color, command=lambda: memory_recall_function(4)).grid(row=6, column=recall_column)
Button(root, text=5, width=5, bg=recall_color, command=lambda: memory_recall_function(5)).grid(row=7, column=recall_column)
Button(root, text=6, width=5, bg=recall_color, command=lambda: memory_recall_function(6)).grid(row=8, column=recall_column)
Button(root, text=7, width=5, bg=recall_color, command=lambda: memory_recall_function(7)).grid(row=9, column=recall_column)
Button(root, text=8, width=5, bg=recall_color, command=lambda: memory_recall_function(8)).grid(row=10, column=recall_column)
Button(root, text=9, width=5, bg=recall_color, command=lambda: memory_recall_function(9)).grid(row=11, column=recall_column)
Button(root, text='A', width=5, bg=recall_color, command=lambda: memory_recall_function('A')).grid(row=12, column=recall_column)
Button(root, text='B', width=5, bg=recall_color, command=lambda: memory_recall_function('B')).grid(row=13, column=recall_column)
Button(root, text='C', width=5, bg=recall_color, command=lambda: memory_recall_function('C')).grid(row=14, column=recall_column)
Button(root, text='D', width=5, bg=recall_color, command=lambda: memory_recall_function('D')).grid(row=15, column=recall_column)
Button(root, text='E', width=5, bg=recall_color, command=lambda: memory_recall_function('E')).grid(row=16, column=recall_column)
Button(root, text='F', width=5, bg=recall_color, command=lambda: memory_recall_function('F')).grid(row=17, column=recall_column)
try:
    with open('preset_labels.txt') as f:
        labels = f.read().splitlines()
    f.close()
except:
    pass
entry_boxes = []
for e in range(16):
    box = Entry(root, justify='right')
    try:
        box.insert(-1, labels[e])
    except:
        pass
    box.grid(row=e+2, column=label_column)
    entry_boxes.append(box)
Button(root, text='Save preset labels', bg=store_color, command=save_preset_labels).grid(row=1, column=label_column)

# Pan and tilt buttons
Button(root, text='↑', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_up)).grid(row=pan_tilt_row, column=pan_tilt_column+1)
Button(root, text='←', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_left)).grid(row=pan_tilt_row+1, column=pan_tilt_column)
Button(root, text='→', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_right)).grid(row=pan_tilt_row+1, column=pan_tilt_column+2)
Button(root, text='↓', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_down)).grid(row=pan_tilt_row+2, column=pan_tilt_column+1)
Button(root, text='↖', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_up_left)).grid(row=pan_tilt_row, column=pan_tilt_column)
Button(root, text='↗', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_up_right)).grid(row=pan_tilt_row, column=pan_tilt_column+2)
Button(root, text='↙', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_down_left)).grid(row=pan_tilt_row+2, column=pan_tilt_column)
Button(root, text='↘', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_down_right)).grid(row=pan_tilt_row+2, column=pan_tilt_column+2)
Button(root, text='■', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_stop)).grid(row=pan_tilt_row+1, column=pan_tilt_column+1)
#Button(root, text='Home', command=lambda: send_message(pan_home)).grid(row=pan_tilt_row+2, column=pan_tilt_column+1)

# Pan speed and Tilt speed
'''
Label(root, text='Pan Speed', bg=pan_tilt_color).grid(row=pan_tilt_row+3, column=pan_tilt_column)
pan_speed_slider = Scale(root, from_=24, to=0, bg=pan_tilt_color)
pan_speed_slider.set(5)
pan_speed_slider.grid(row=pan_tilt_row+4, column=pan_tilt_column, rowspan=4)
Label(root, text='Tilt Speed', bg=pan_tilt_color).grid(row=pan_tilt_row+3, column=pan_tilt_column+1)
tilt_speed_slider = Scale(root, from_=24, to=0, bg=pan_tilt_color)
tilt_speed_slider.set(5)
tilt_speed_slider.grid(row=pan_tilt_row+4, column=pan_tilt_column+1, rowspan=4)
#Button(root, text='test pan speed', command=lambda: pan()).grid(row=pan_tilt_row+5, column=pan_tilt_column+1)

# slider to set speed for pan_speed and tilt_speed (0x01 to 0x17)
# still not quite sure about this...
#Scale(root, from_=0, to=17, variable=movement_speed, orient=HORIZONTAL, label='Speed').grid(row=5, column=2, columnspan=3)
#'''

# Zoom buttons
Label(root, text='Zoom', bg=zoom_color, width=button_width).grid(row=zoom_row, column=zoom_column)
Button(root, text='In', bg=zoom_color, width=button_width, command=lambda: send_message(zoom_tele)).grid(row=zoom_row+1, column=zoom_column)
Button(root, text='Stop', bg=zoom_color, width=button_width, command=lambda: send_message(zoom_stop)).grid(row=zoom_row+2, column=zoom_column)
Button(root, text='Out', bg=zoom_color, width=button_width, command=lambda: send_message(zoom_wide)).grid(row=zoom_row+3, column=zoom_column)
# Focus buttons
#Label(root, text='Focus', width=button_width, bg=focus_color).grid(row=focus_row, column=focus_column)
#Button(root, text='Near', width=button_width, bg=focus_color, command=lambda: send_message(focus_near)).grid(row=focus_row+1, column=focus_column)
#Button(root, text='Far', width=button_width, bg=focus_color, command=lambda: send_message(focus_far)).grid(row=focus_row+2, column=focus_column)

# On off connect buttons
Label(root, text='Camera', bg=on_off_color, width=button_width).grid(row=on_off_row, column=on_off_column)
Button(root, text='On', bg=on_off_color, width=button_width, command=lambda: send_message(camera_on)).grid(row=on_off_row+1, column=on_off_column)
Button(root, text='Connect', bg=on_off_color, width=button_width, command=reset_sequence_number_function()).grid(row=on_off_row+2, column=on_off_column)
Button(root, text='Off', bg=on_off_color, width=button_width, command=lambda: send_message(camera_off)).grid(row=on_off_row+3, column=on_off_column)
Button(root, text='Info Off', bg=on_off_color, width=button_width, command=lambda: send_message(information_display_off)).grid(row=on_off_row+4, column=on_off_column)

# IP Label
#Label(root, text=camera_ip+':'+str(camera_port)).grid(row=6, column=0, columnspan=3)
# Connection Label
#Label(root, textvariable=display_message).grid(row=6, column=4, columnspan=3)

root.mainloop()
