import json
import websocket

class Message:
    def __init__(self, data):
        assert type(data) == dict
        self._data = data

    def __contains__(self, key): return key in self._data
    def __getattr__(self, key): return self._data[key]
    def __repr__(self): return "Message({0})".format(self._data)

class Socket:
    def __init__(self, endpoint, **params):
        # TODO make base URL configurable
        # TODO do proper URL handling
        baseUrl = 'ws://localhost:8080/v0.10'
        paramStr = '&'.join('{0}={1}'.format(k,v) for k, v in params.items())
        self._url = '{baseUrl}{endpoint}/websocket?{paramStr}'.format(**locals())
        self._ws = websocket.WebSocketApp(self._url,
            on_message=self._onMessage,
            on_error=self._onError,
            on_open=self._onOpen,
            on_close=self._onClose)

    def _onMessage(self, ws, messageText):
        msg = Message(json.loads(messageText))
        print("<< {0}".format(messageText))
        self.onMessage(msg)

    def _onClose(self, ws):
        print("onClose:")
        print("  ws={0}".format(ws))
        print("  url={0}".format(self._url))

    def _onError(self, ws, error):
        print("onError:")
        print("  ws={0}".format(ws))
        print("  error={0}".format(error))

    def _onOpen(self, ws):
        print("onOpen:")
        print("  ws={0}".format(ws))
        print("  url={0}".format(self._url))
        if (hasattr(self, 'onOpen')):
            self.onOpen(self)

    def close(self):
        self._ws.close()

    def run(self):
        self._ws.run_forever()

    def send(self, data):
        self._ws.send(data)
