# pip3 install aiosc
# https://pypi.org/project/aiosc
# https://github.com/artfwo/aiosc

import asyncio
import aiosc


#''' sending works
touchOSC_ip = '10.0.0.30'
touchOSC_port = 9000
osc_command = 'pan_tilt_speed_label'
osc_argument = 5

loop = asyncio.get_event_loop()
#loop.run_until_complete(aiosc.send((touchOSC_ip, touchOSC_port), '/1/pan_tilt_speed', 5))
#loop.run_until_complete(aiosc.send((touchOSC_ip, touchOSC_port), '/1/'+osc_command, osc_argument))
loop.run_until_complete(aiosc.send(('10.0.0.201', 9000), '/ch/01/mix/fader', 0.5))
#'''
print('complete')

''' server works
def print_message(addr, path, args):
    if args[0] == 1.0:
        print(path)
    #print(args[0])


# OSC receiving server
def protocol_factory():
    osc = aiosc.OSCProtocol({'//*': lambda addr, path, *args: print_message(addr, path, args)})
    return osc

loop = asyncio.get_event_loop()
coro = loop.create_datagram_endpoint(protocol_factory, local_addr=('0.0.0.0', 8000))
transport, protocol = loop.run_until_complete(coro)
loop.run_forever()
'''
