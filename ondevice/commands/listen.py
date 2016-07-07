"""
Starts the ondevice daemon in the foreground.
"""

from ondevice.core import config
from ondevice.core.session import Session

import logging
import sys
import time

def run(__sentinel__=None, auth=None):
    if __sentinel__ != None:
        raise Exception("Too many arguments")

    retryDelay = 10

    while (True):
        # TODO think about moving the loop into Session
        # TODO right now it's impossible to reuse Session objects (since the URL's set in the constructor but the devId might change afterwards)
        session = Session(auth)
        if session.run() == True:
            retryDelay = 10

        logging.info("Lost connection, retrying in %ds", retryDelay)
        time.sleep(retryDelay)
        retryDelay = min(900, retryDelay*1.5)

def usage():
    return "<auth=accountKey> [dev=devId]", "Starts the ondevice daemon in the foreground"
