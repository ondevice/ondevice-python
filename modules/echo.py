from core.connection import Connection, Response
from modules import Endpoint

import codecs
import sys
import threading

class Client(Endpoint):
    def gotData(self, data):
        sys.stdout.buffer.write(b"> "+data)
        sys.stdout.flush()

    def runLocal(self):
        while True:
            data = sys.stdin.buffer.readline()
            if data:
                #print("sndData: {0}".format(codecs.encode(data, 'hex')))
                self._conn.send(data)
            else:
                #print("EOF (TODO: do sth about it)")
                self._conn.close()
                return

class Service(Endpoint):
    def __init__(self, request, devId):
        self._devId = devId
        self._request = request

    def runLocal(self):
        pass

    def gotData(self, data):
        self._conn.send(data)
