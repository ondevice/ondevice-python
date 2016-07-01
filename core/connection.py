from core import sock


class Connection(sock.Socket):
    def __init__(self, dev, protocol, service, cb=None, auth=None):
        super().__init__('/connect', auth=auth, dev=dev, protocol=protocol, service=service)
        # TODO implement proper URL handling
        self._cb = cb

    def _onMessage(self, ws, messageData):
        return self._cb(messageData)


class Response(sock.Socket):
    def __init__(self, broker, tunnelId, dev, cb=None):
        super().__init__('/accept', tunnel=tunnelId, dev=dev)
        self._cb = cb

    def _onMessage(self, ws, messageData):
        return self._cb(messageData)
