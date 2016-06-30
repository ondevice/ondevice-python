import websocket

class Connection:
    def __init__(self, dev, protocol, service, url='ws://localhost:8080/v0.10/connect/websocket', cb=None, auth=None):
        # TODO implement proper URL handling
        self._url = '{0}?auth={1}&dev={2}&protocol={3}&service={4}'.format(url, auth, dev, protocol, service)
        self._cb = cb
        self._ws = websocket.WebSocketApp(self._url,
			on_message=self._onMessage,
			on_error=self._onError,
			on_open=self._onOpen,
			on_close=self._onClose)

    def _onClose(self, ws):
        print("onClose:")
        print("  ws={0}".format(ws))

    def _onError(self, ws, error):
        print("onError:")
        print("  ws={0}".format(ws))
        print("  error={0}".format(error))

    def _onMessage(self, ws, messageData):
        return self._cb(ws, messageData)

    def _onOpen(self, ws):
        print("onOpen:")
        print("  ws={0}".format(ws))

    def run(self):
        self._ws.run_forever()

    def send(self, data):
        return
