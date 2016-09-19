"""
Prints the client version and ondeviceID (if the daemon is running).

Note that this command will include further information (like the daemon version
in case we're querying a non-local daemon) in the future.

Returns:
- 0 if the daemon is running
- 1 if it isn't
- >1 on errors (in the future)
"""

import ondevice
from ondevice.core import config, daemon

import psutil

usage = {
    'msg': 'prints information on the ondevice client and daemon',
}

def run():
    devId = None
    if daemon.getDaemonPID() != None:
        devId = config.getDeviceId()

    if devId != None:
        print("Device:")
        print("  ID: {0}".format(devId))

    print("Client:")
    print("  version: {0}".format(ondevice.getVersion()))

    return 0 if devId != None else 1
