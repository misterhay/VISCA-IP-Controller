'''
POS_1=["1200","EF00"]
POS_2=["ED00","0400"]
sequence_number = 1

payload = "81 01 06 02 " #Movetoabsoluteposition in POS
payload = payload + '15 ' + ' 15 ' #add move speed
for i in POS_1: #add position
    for j in i:
        payload = payload + "0" + j +" "
payload = payload + "FF " #end byte

header = "01 00 " # Payload type : 0100 for a command, 0110 for and inquiry, 0200 for a control command and 0120 for a device setting command
header = header + "00 "
#header = header + ('0'*(4-len(hex(len(payload.replace(' ',''))//2))) +hex(len(payload.replace(' ',''))//2))
header=header + '0F '
header = header + ('0'*(8-len(str(sequence_number)))+str(sequence_number)) 


message = header + payload
#sock.sendto(bytes.hex(message.replace(' ','')))
#print("message = " + bytes.hex(message.replace(' ','')))
print('message =', bytes.fromhex(message.replace(' ','')))
other_message = message
#'''

'''
payload_type = '01 00' # 0100 command, 0110 inquiry, 0200 control, and 0120 device settings
#payload_length = '00 05'
sequence_number = '00 00 00 01' # iterate this up to FF FF FF FF then loop back to 00 00 00 00
payload = '81 01 04 00 02 FF'.replace(' ', '')
payload_length = '00 0' + str(int(len(payload)/2))
message_string = payload_type + payload_length + sequence_number + payload # + end_byte
message = bytes.fromhex(message_string.replace(' ',''))
#s.sendto(message, (ip, port))
print('Sent', message)
'''


# I think this works
i = 0
while i < 2:
    payload_type = bytearray.fromhex('01 00')
    #payload = bytearray.fromhex('81 01 04 07 24 FF') # zoom in, this continues to max zoom
    #payload = bytearray.fromhex('81 01 04 00 03 FF') # off
    payload = bytearray.fromhex('81 01 04 00 02 FF') # on
    sequence_number = i.to_bytes(4, 'big')
    payload_length = len(payload).to_bytes(2, 'big')
    message = payload_type + payload_length + sequence_number + payload
    print(message)
    i += 1
    #s.sendto(bytes.hex(message.replace(' ','')))
#'''

# b'\x01\x00\x00\x0f\x00\x00\x00\x01\x81\x01\x06\x02\x15\x15\x01\x02\x00\x00\x0e\x0f\x00\x00\xff'

reset_sequence_number_message = bytearray.fromhex('02 00 00 01 00 00 00 01 01')

import socket

ip = '192.168.0.100'
#ip = '127.0.0.1'
port = 52381
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
s.sendto(reset_sequence_number_message,(ip, port))
s.sendto(message, (ip, port))
