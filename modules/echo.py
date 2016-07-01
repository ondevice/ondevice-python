from core.connection import Connection, Response

import codecs
import sys
import threading

class Client:
    def __init__(self, dev, svcName, auth=None):
        if auth == None:
            raise Exception("Missing auth key!")
        self._conn = Connection(dev, 'echo', svcName, auth=auth, cb=self._gotData)

    def connect(self):
        self._thread = threading.Thread(target=self._readStdin)
        self._thread.start()
        self._conn.run()

    def _gotData(self, data):
        sys.stdout.buffer.write(b"> "+data)
        sys.stdout.flush()

    def _readStdin(self):
        while True:
            data = sys.stdin.buffer.readline()
            if data:
                #print("sndData: {0}".format(codecs.encode(data, 'hex')))
                self._conn.send(data)
            else:
                #print("EOF (TODO: do sth about it)")
                self._conn.close()
                return

class Service:
    def __init__(self, request, devId):
        print ("got incoming echo connection request: {0}".format(request))
        self._devId = devId
        self._request = request

    def run(self):
        req = self._request
        self._resp = Response('broker', req.tunnelId, self._devId, self._gotData)
        self._resp.run()

    def _gotData(self, data):
        self._resp.send(data)
