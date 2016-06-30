"""
Starts the ondevice daemon in the foreground.
"""

from core.session import Session

def run(__sentinel=None, auth=None, dev=None):
    if __sentinel != None:
        raise Exception("Too many arguments")
    if auth == None:
        # TODO persist the user key
        raise Exception("Missing authentication key!")
    if dev == None:
        raise Exception("Missing device ID")
    session = Session(auth, dev)
    session.run()

def usage():
    return "<auth=accountKey> [dev=devId]", "Starts the ondevice daemon in the foreground"
