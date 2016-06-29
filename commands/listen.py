"""
Starts the ondevice daemon in the foreground.
"""

from core.session import Session

def run():
    session = Session()
    session.run()

def usage():
    return "", "Starts the ondevice daemon in the foreground"
