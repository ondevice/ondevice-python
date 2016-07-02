"""
Starts the ondevice daemon in the foreground.
"""

from core import config
from core.session import Session

import logging
import sys

def run(__sentinel__=None, auth=None):
    if __sentinel__ != None:
        raise Exception("Too many arguments")

    session = Session(auth)
    session.run()

def usage():
    return "<auth=accountKey> [dev=devId]", "Starts the ondevice daemon in the foreground"
