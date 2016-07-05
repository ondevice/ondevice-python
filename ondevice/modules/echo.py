from ondevice.core.connection import Connection, Response
from ondevice.modules import Endpoint

import codecs
import six
import sys
import threading

class Client(Endpoint):
    def gotData(self, data):
        stream = self.getConsoleBuffer(sys.stdout)
        stream.write(b"> "+data)
        stream.flush()

    def runLocal(self):
        stream = self.getConsoleBuffer(sys.stdin)
        while True:
            data = stream.readline()
            if data:
                #print("sndData: {0}".format(codecs.encode(data, 'hex')))
                self._conn.send(data)
            else:
                self._conn.sendEOF()
                return

class Service(Endpoint):
    def __init__(self, request, devId):
        self._devId = devId
        self._request = request

    def runLocal(self):
        pass

    def gotData(self, data):
        self._conn.send(data)
