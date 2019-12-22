







''' not working
from oscpy.server import OSCThreadServer
from time import sleep

def callback(values):
    print(values)
    print("got values: {}".format(values))

osc = OSCThreadServer()
sock = osc.listen(address='0.0.0.0', port=8000, default=True)
osc.bind(b'/1/PanTiltButtons', callback)
sleep(1000)
osc.stop()
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