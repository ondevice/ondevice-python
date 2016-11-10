"""
Prints the client version and ondeviceID (if the daemon is running).

Note that this command will include further information (like the daemon version
in case we're querying a non-local daemon) in the future.

Returns:
- 0 if the daemon is running and online
- 1 if the daemon is running, but offline/reconnecting
- 2 if the daemon is not running
- >2 on errors
"""

import ondevice
from ondevice.core import daemon, exception
from ondevice.control import client

import getopt
import json
import logging

usage = {
    'msg': 'prints information on the ondevice client and daemon',
}

def run(*args):
    jsonOutput = False
    rc = 2 # assume it's not running

    # parse commandline arguments
    opts, args = getopt.gnu_getopt(args, '', ('json'))
    for k,v in opts:
        if k == '--json':
            jsonOutput = True

    state = client.Data({
        'client': {
            'version': ondevice.getVersion()
        }
    })
    
    try:
        s = client.getState(False)
        s._data.update(state._data)
        state = s
        
        rc = 1 # daemon is responding

        if 'device' in state:
            if state.device.state == 'online':
                rc = 0

    except exception.TransportError as e:
        # TODO actually check if the ondevice daemon is running (or if it was some other kind of TransportError)
        rc = 2
    except Exception as e:
        # TODO improve error handling
        logging.error("Caught exception")
        rc = 2

    # output
    if jsonOutput:
        print(json.dumps(state._data, indent=4))
    else:
        if 'version' in state:
            print("Daemon:")
            print("  version: {0}".format(state.version))
            
        if 'device' in state:
            print("  deviceID: {0}".format(state.device.devId))
            print("")
        print("Client:")
        print("  version: {0}".format(ondevice.getVersion()))

    return rc