import asyncio
import socket

port = 52381
buffer_size = 1024

receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_socket.bind(('', port))

async def socket_receive():
    print("Doing the socket thing")
    while True:
        socket_data = receive_socket.recvfrom(buffer_size)
        print(socket_data)
    await asyncio.sleep(1)

async def osc_receive():
    print("Doing the osc thing")

    await asyncio.sleep(2)
'''
async def main():
    while True:
        await socket_receive()
        await osc_receive()
'''
loop = asyncio.get_event_loop()
#loop.create_task(main())
loop.create_task(socket_receive())
loop.create_task(osc_receive)
loop.run_forever()