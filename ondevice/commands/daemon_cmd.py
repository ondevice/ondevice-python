"""
Run the ondevice daemon.

See also: `ondevice help listen` (deprecated variant of `ondevice daemon`
that stays in the foreground)
"""

usage = {
    'msg': 'Run the ondevice daemon',
    'group': 'device'
}

from ondevice.core import daemon

from daemon import DaemonContext

def run():
    with DaemonContext():
        daemon.runForever()
