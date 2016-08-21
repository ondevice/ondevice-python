import ondevice

from six.moves import urllib_parse
import base64
import json
import logging
import ssl
import websocket

BASE_URL=urllib_parse.urlparse('wss://api.ondevice.io/v1.1')
#BASE_URL=urllib_parse.urlparse('ws://localhost:8080/v1.1')
#BASE_URL=urllib.parse.urlparse('wss://local.ondevice.io:8443/v1.1')
class Message:
    def __init__(self, data):
        assert type(data) == dict
        self._data = data

    def __contains__(self, key): return key in self._data
    def __getattr__(self, key): return self._data[key]
    def __repr__(self): return "Message({0})".format(self._data)

class Socket:
    def __init__(self, endpoint, baseUrl=None, auth=None, **params):
        global BASE_URL

        # TODO make base URL configurable
        # TODO do proper URL handling
        if baseUrl == None:
            baseUrl = BASE_URL.geturl()

        paramStr = '&'.join('{0}={1}'.format(k,v) for k, v in params.items())
        self._url = '{baseUrl}{endpoint}/websocket?{paramStr}'.format(**locals())

        headers = []
        headers.append('User-agent: ondevice v{0}'.format(ondevice.getVersion()))
        if auth != None:
            basicAuth = "{0}:{1}".format(*auth).encode('ascii')
            headers.append("Authorization: Basic {0}".format(base64.b64encode(basicAuth).decode('ascii')))
        else:
            raise Exception("Missing authentication data")

        self._ws = websocket.WebSocketApp(self._url,
            header=headers,
            on_message=self._onMessage,
            on_error=self._onError,
            on_open=self._onOpen,
            on_close=self._onClose)

    def _getSslVersion(self):
        """ In python2.6 the protocol setting PROTOCOL_SSLv23 doesn't include TLS.
        This method works around that issue by only selecting PROTOCOL_SSLv23 if
        PROTOCOL_TLSv1_1 is available """
        if hasattr(ssl, 'PROTOCOL_TLSv1_1'):
            # Python >= 2.7.9 + openssl >= 1.0.1 -> SSLv23 is safe
            return ssl.PROTOCOL_SSLv23
        else:
            # there's no TLSv1.1+ support -> force TLSv1.0
            return ssl.PROTOCOL_TLSv1

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
        # Python2.6 fix (its ssl module won't try TLSv1 unless we explicitly tell it to)
        sslopt = {'ssl_version': self._getSslVersion()}

        self._ws.run_forever(sslopt=sslopt)

    def send(self, data):
        self._ws.send(data)
