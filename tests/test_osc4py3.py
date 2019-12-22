# https://pypi.org/project/osc4py3/
# pip3 install osc4py3

# Receiving  https://osc4py3.readthedocs.io/en/latest/userdoc.html#quick-osc
from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm

def handlerfunction(s, x, y):
    # Will receive message data unpacked in s, x, y
    print(s, x, y)
    pass

def handlerfunction2(address, s, x, y):
    # Will receive message address, and message data flattened in s, x, y
    pass

# Start the system.
osc_startup()

# Make server channels to receive packets.
osc_udp_server("0.0.0.0", 8000, "aservername")

# Associate Python functions with message address patterns, using default
# argument scheme OSCARG_DATAUNPACK.
osc_method("/*", handlerfunction)
# Too, but request the message address pattern before in argscheme
#osc_method("/1/*", handlerfunction2, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

# Periodically call osc4py3 processing method in your event loop.
finished = False
while not finished:
    # …
    osc_process()
    # …

# Properly close the system.
osc_terminate()