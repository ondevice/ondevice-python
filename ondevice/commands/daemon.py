"""
Run the ondevice daemon.
"""

usage = {
    'msg': 'Run the ondevice daemon',
    'group': 'device'
}

from ondevice.core import session

import daemon

def run():
    with daemon.DaemonContext():
        session.runForever()
