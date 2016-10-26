"""
Prints the client version and ondeviceID (if the daemon is running).

Note that this command will include further information (like the daemon version
in case we're querying a non-local daemon) in the future.

Returns:
- 0 if the daemon is running
- 1 if it isn't
- >1 on errors
"""

import ondevice
from ondevice.core import daemon, exception
from ondevice.control import client

import logging

usage = {
    'msg': 'prints information on the ondevice client and daemon',
}

def run():
    rc = 0

    try:
        state = client.getState(False)
        if 'device' in state:
            print("Device:")
            print("  ID: {0}".format(state.device.devId))
            if state.device.state != 'online':
                rc = 1
        else:
            rc = 1

    except exception.TransportError as e:
        # TODO actually check if the ondevice daemon is running (or if it was some other kind of TransportError)
        rc = 1
    except Exception as e:
        # TODO improve error handling
        logging.error("Caught exception")
        rc = 2

    print("Client:")
    print("  version: {0}".format(ondevice.getVersion()))

    return rc