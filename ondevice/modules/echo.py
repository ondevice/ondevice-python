from ondevice.core.connection import Connection, Response
from ondevice.modules import TunnelClient, TunnelService

import codecs
import six
import sys
import threading

class Client(TunnelClient):
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

class Service(TunnelService):
    def runLocal(self):
        pass

    def gotData(self, data):
        self._conn.send(data)
