import json
import logging
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
        logging.debug("<< %s", messageText)
        self.onMessage(msg)

    def _onClose(self, ws):
        logging.debug("onClose:")
        logging.debug("  ws=%s", ws)

    def _onError(self, ws, error):
        logging.error("onError:")
        logging.error("  ws=%s", ws)
        logging.error("  error=%s", error)

    def _onOpen(self, ws):
        logging.debug("onOpen:")
        logging.debug("  ws=%s", ws)
        if (hasattr(self, 'onOpen')):
            self.onOpen(self)

    def close(self):
        self._ws.close()

    def run(self):
        self._ws.run_forever()

    def send(self, data):
        self._ws.send(data)
