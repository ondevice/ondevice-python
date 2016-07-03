"""
Starts the ondevice daemon in the foreground.
"""

from core import config
from core.session import Session

import logging
import sys
import time

def run(__sentinel__=None, auth=None):
    if __sentinel__ != None:
        raise Exception("Too many arguments")

    session = Session(auth)
    while (True):
        # TODO think about moving this into Session
        if session.run() == True:
            retryDelay = 5
        else:
            retryDelay = min(900, retryDelay*1.5)
        logging.info("Lost connection, retrying in %ds", retryDelay)
        time.sleep(retryDelay)

def usage():
    return "<auth=accountKey> [dev=devId]", "Starts the ondevice daemon in the foreground"
