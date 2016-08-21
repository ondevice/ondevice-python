""" Simple echo module (responds with the same data it gets)

The idea of this module is to provide both a test module to test connections and
an example module for you to base your own module implementations on.

See the [yet to be written - the module infrastructure is not considered stable
yet] module implementation guide.
"""

from ondevice.modules import ModuleClient, ModuleService

import sys

# short module description that will be shown when users type `ondevice modules`
info = 'Simple test module that sends back what it receives'
# Indicates whether or not the underlying protocol is itself encrypted.
encrypted = False

class Client(ModuleClient):
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
                self._conn.send(data)
            else:
                self._conn.sendEOF()
                return

class Service(ModuleService):
    def runLocal(self):
        pass

    def onMessage(self, data):
        self._conn.send(data)
