# https://pro.sony/s3/2019/01/16020225/AES6100121.pdf

import socket

#ip = '10.0.0.42'
ip = '127.0.0.1'
port = 52381 # or maybe 52380
buffer_size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
sequence_number = 1 # a global variable that we'll iterate each command
# but 0, 0, 0, 1

'''
x = 1 for first command buffer, x = 2 for second (only 2)
ASCII

Prefix:
0x01 0x00 0x00 0x05 0x00 0x00 0x00 0x01
01 00 means Payload type (VISCA command) or 01 20 for VISCA device setting
00 05 means Payload length (5 in this example)
00 00 00 01 means sequence number (this should be iterated)

CAM_Power on   8x 01 04 00 02 FF
CAM_Power off  8x 01 04 00 03 FF

CAM_Memory recall  8x 01 04 3F 02 0p FF  # p is 0 to F
CAM_Memory set     8x 01 04 3F 01 0p FF  # p is 0 to F

Pan-tiltDrive home  8x 01 06 04 FF
'''

def testing():
    message = b'\x81\x01\x04\x00\x02\xFF' # power on
    s.sendto(message, (ip, port))
    print('Sent', message)

def memory_recall(memory_number): # memory_number is 0 to F
    #message_string = '\x81\x01\x04\x3F\x02\x0'+memory_number+'\xFF'
    message_string = '81 01 04 00 02 FF'
    message = bytes(message_string, 'ASCII')
    s.sendto(message, (ip, port))
    print('Sent', message, 'for memory number', memory_number)

def create_message(command): # exclude the 8x 01 part and the FF at the end
    global sequence_number
    #payload = []
    payload = [129, 1] # 129 is 81 in hex
    payload.extend(command)
    payload.extend([255])
    #print(payload)
    m = []
    m.extend([1, 0]) # payload type
    #print(len(payload))
    m.extend([0, len(payload)]) # payload length
    m.extend([0, 0, 0, sequence_number]) # sequence number
    m.extend(payload)
    #print(m)
    message = bytearray(m)
    sequence_number += 1
    if sequence_number > 15:
        sequence_number = 0
    return message

def send_message(message):
    s.sendto(message, (ip, port))
    print('Sent', message)
    return message

def create_and_send_message(command):
    message = create_message(command)
    #print(message)
    send_message(message)
    return message

'''
command = [4, 0, 2] # power on
#command = [4, 9, 2, 0] # memory recall, last number is 0 to 15
message = create_message(command)
print(message)
send_message(message)
'''

from tkinter import *
root = Tk()
Label(root, text='VISCA IP Camera Controller').grid(row=0, columnspan=100)
Button(root, text=1, command=lambda: create_and_send_message([4, 9, 2, 0])).grid(row=1, column=0)
Button(root, text=2, command=lambda: create_and_send_message([4, 9, 2, 1])).grid(row=1, column=1)
Button(root, text=3, command=lambda: create_and_send_message([4, 9, 2, 2])).grid(row=2, column=0)
Button(root, text=4, command=lambda: create_and_send_message([4, 9, 2, 3])).grid(row=2, column=1)
Button(root, text=5, command=lambda: create_and_send_message([4, 9, 2, 4])).grid(row=3, column=0)
Button(root, text=6, command=lambda: create_and_send_message([4, 9, 2, 5])).grid(row=3, column=1)
Button(root, text='Home', command=lambda: create_and_send_message([6, 4])).grid(row=4, column=0, columnspan=2, sticky=S)

Button(root, text='Up', command=lambda: create_and_send_message([])).grid(row=1, column=3)
Button(root, text='Left', command=lambda: create_and_send_message([])).grid(row=2, column=2)
Button(root, text='Right', command=lambda: create_and_send_message([])).grid(row=2, column=4)
Button(root, text='Down', command=lambda: create_and_send_message([])).grid(row=3, column=3)

Button(root, text='In', command=lambda: create_and_send_message([4, 7, 2])).grid(row=3, column=5)
Button(root, text='Out', command=lambda: create_and_send_message([4, 7, 3])).grid(row=4, column=5)

Button(root, text='On', command=lambda: create_and_send_message([4, 0, 2])).grid(row=1, column=6)

Label(root, text='8x,1,').grid(row=5, column=0)
e = Entry(root).grid(row=5, column=1, columnspan=4)
list_from_entry = []
Button(root, text='Send', command=lambda: create_and_send_message(list_from_entry)).grid(row=5, column=4)
root.mainloop()