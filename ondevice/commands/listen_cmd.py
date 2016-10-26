"""
Starts the ondevice daemon in the foreground.

This is a legacy command, provided for backwards compatibility.
Use `ondevice daemon` instead where possible
"""

usage = {
    'msg': 'Like `daemon`, but in the foreground',
    'group': 'device',
    'hidden': True
}

from ondevice.core import daemon
from ondevice import control

def run():
    control.server.start()
    daemon.runForever()
    control.server.stop()
