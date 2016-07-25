"""
Starts the ondevice daemon in the foreground.
"""

usage = {
    'msg': 'Like `daemon`, but in the foreground',
    'group': 'device'
}

from ondevice.core import session

def run():
    session.runForever()
