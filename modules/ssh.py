from core.connection import Connection, Response
from modules import Endpoint

import codecs
import logging
import socket
import subprocess
import sys
import threading

class Client(Endpoint):
    def gotData(self, data):
        logging.debug("gotData: %s", repr(data))
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()

    def runLocal(self):
        while True:
            # read1() only invokes the underlying read function only once (and
            # in contrast to read() returns as soon as there's data available,
            # not just when 8192 bytes have actually been read)
            data = sys.stdin.buffer.read1(8192)
            if data:
                logging.debug("sndData: %s", repr(data))
                self._conn.send(data)
            else:
                logging.info("Local EOF, closing connection")
                self._conn.sendEOF()
                return

class Service(Endpoint):
    def __init__(self, request, devId):
        self._devId = devId
        self._request = request

    def runLocal(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO make me configurable
        # TODO use a timeout; raise an exception on error
        self._sock.connect(('localhost', 22))

        while True:
            data = self._sock.recv(8192)
            if data:
                logging.debug("sndData: %s", repr(data))
                self._conn.send(data)
            else:
                self._conn.sendEOF()
                return

    def gotData(self, data):
        logging.debug("gotData: %s", repr(data))
        self._sock.send(data)
