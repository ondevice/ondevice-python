""" Simple echo module (responds with the same data it gets)

The idea of this module is to provide both a test module to test connections and
an example module for you to base your own module implementations on.

See the [yet to be written - the module infrastructure is not considered stable
yet] module implementation guide.
"""

from ondevice.core.connection import Connection, Response
from ondevice.modules import TunnelClient, TunnelService

import codecs
import six
import sys
import threading

# short module description that will be shown when users type `ondevice modules`
info = 'Simple test module that sends back what it receives'
# Indicates whether or not the underlying protocol is itself encrypted.
encrypted = False

class Client(TunnelClient):
    def onClose(self):
        self.getConsoleBuffer(sys.stdin).close()

    def onEOF(self):
        self.getConsoleBuffer(sys.stdout).close()

    def onMessage(self, data):
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

    def onMessage(self, data):
        self._conn.send(data)
