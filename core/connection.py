from core import config, sock


class Connection(sock.Socket):
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

    def _onMessage(self, ws, messageData):
        return self._cb(messageData)

    def send(self, msg):
        if (type(msg) == bytes):
            self._ws.send(msg, 2) # OPCODE_BINARY
        else:
            self._ws.send(msg, 1) # OPCODE_TEXT

class Response(sock.Socket):
    def __init__(self, broker, tunnelId, dev, cb=None):
        super().__init__('/accept', tunnel=tunnelId, dev=dev)
        self._cb = cb

    def _onMessage(self, ws, messageData):
        return self._cb(messageData)

    def send(self, msg):
        if (type(msg) == bytes):
            self._ws.send(msg, 2) # OPCODE_BINARY
        else:
            self._ws.send(msg, 1) # OPCODE_TEXT
