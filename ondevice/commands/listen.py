"""
Starts the ondevice daemon in the foreground.
"""

from ondevice.core import session

def run(__sentinel__=None, auth=None):
    # TODO properly implement --user and --auth param support
    if __sentinel__ != None:
        raise Exception("Too many arguments")

    session.runForever()

def usage():
    return "[dev=devId]", "Starts the ondevice daemon in the foreground"
