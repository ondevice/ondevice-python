from core import config, sock

import logging
import threading

class TunnelSocket(sock.Socket):
    """ Base class for Connection and Response """
    def __init__(self, *args, **kwargs):
        self._lock = threading.Lock()
        self._lock.acquire()
        super().__init__(*args, **kwargs)

    def _onMessage(self, ws, messageData):
        logging.debug(b'<< '+messageData)
        return self._cb(messageData)

    def _onOpen(self, ws):
        self._lock.release()
        super()._onOpen(ws)

    def send(self, msg):
        self._lock.acquire()
        logging.debug(b'>> '+msg)
        if (type(msg) == bytes):
            self._ws.send(msg, 2) # OPCODE_BINARY
        else:
            self._ws.send(msg, 1) # OPCODE_TEXT
        self._lock.release()


class Connection(TunnelSocket):
    def __init__(self, dev, protocol, service, cb=None, auth=None):
        self._cb = cb

        if auth != None:
            config.setClientAuth(auth)
        else:
            auth = config.getClientAuth()
            if auth == None:
                logging.error("Missing authentication key. You'll have to set it once using the 'auth=...' param")
                sys.exit(1)

        super().__init__('/connect', auth=auth, dev=dev, protocol=protocol, service=service)


class Response(TunnelSocket):
    def __init__(self, broker, tunnelId, dev, cb=None):
        super().__init__('/accept', tunnel=tunnelId, dev=dev)
        self._cb = cb
