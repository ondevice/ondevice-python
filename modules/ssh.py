from core.connection import Connection, Response

import codecs
import socket
import threading

class Client:
    def __init__(self, dev, svcName, auth=None):
        if auth == None:
            raise Exception("Missing auth key!")
        self._conn = Connection(dev, 'ssh', svcName, auth=auth, cb=self._gotData)

    def connect(self):
        self._conn.run()

    def _gotData(self, ws, data):
        print("-- got data: {0}".format(data))

class Service:
    def __init__(self, request, devId):
        print ("got incoming SSH connection request: {0}".format(request))
        self._devId = devId
        self._request = request

    def run(self):
        req = self._request
        self._resp = Response('broker', req.client, self._devId, self._gotData)
        self._resp.onOpen = self._onOpen
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._resp.run()

    def _gotData(self, ws, data):
        print("gotData: {0}".format(codecs.encode(data, 'hex')))
        self._sock.write(data)

    def _onOpen(self, ws):
        # TODO make me configurable
        # TODO use a timeout; raise an exception on error
        self._sock.connect(('localhost', 22))

        self._thread = threading.Thread(target=self._readSocket)
        self._thread.start()

    def _readSocket(self):
        while True:
            data = self._sock.recv(8192)
            if data:
                print("sndData: {0}".format(codecs.encode(data, 'hex')))
                self._resp.send(data)
            else:
                print("eof!?!")
                return
