import ondevice
from ondevice.core import config

import base64
import json
import logging
import ssl
import websocket

try:
    from http.client import HTTPConnection, HTTPSConnection
except ImportError:
    from httplib import HTTPConnection, HTTPSConnection

BASE_URL='wss://api.ondevice.io/v1.1'
#BASE_URL='ws://localhost:8080/v1.1'
#BASE_URL='wss://local.ondevice.io:8443/v1.1'
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
            baseUrl = BASE_URL

        if 'version' not in params:
            params['version'] = ondevice.getVersion()

        paramStr = '&'.join('{0}={1}'.format(k,v) for k, v in params.items())
        self._url = '{baseUrl}{endpoint}/websocket?{paramStr}'.format(**locals())

        headers = []
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

def apiDELETE(endpoint, params={}, data=None):
    return apiRequest('DELETE', endpoint, params=params, data=data)

def apiGET(endpoint, params={}):
    return apiRequest('GET', endpoint, params=params)

def apiPOST(endpoint, params={}, data=None):
    return apiRequest('POST', endpoint, params=params, data=data)

def apiRequest(method, endpoint, params={}, data=None):
    # TODO implement URL params support
    auth = config.getClientAuth()
    basicAuth = base64.b64encode("{0}:{1}".format(*auth).encode('ascii')).decode('ascii')
    headers = { 'Authorization' : 'Basic {0}'.format(basicAuth)}

    # parse data:
    if data != None:
        data = json.dumps(data)
        headers.update({
            'Content-type': 'application/json; charset=utf8',
        }) # TODO check if we need to also set the content-length

    # TODO use the BASE_URL
    c = HTTPSConnection("api.ondevice.io")
    # TODO do proper URL handling (urllib)
    c.request(method, '/v1.1{0}'.format(endpoint), body=data, headers=headers)
    resp = c.getresponse()
    rc = resp.read()

    if resp.status < 200 or resp.status >= 300:
        # TODO implement HTTP redirect support
        logging.warning("Error message: %s", rc)
        raise Exception("API server responded with code {0}!".format(resp.status))
    elif 'content-type' not in resp.headers:
        raise Exception("Response lacks Content-type header!")

    cType=resp.headers['content-type'].lower().split(';')
    if cType[0] != 'application/json':
        raise Exception("Expected an 'application/json' response (was: '{0}')".format(cType[0]))
    if type(rc) == bytes:
        rc = rc.decode('utf8') # TODO check the actual 'charset' part from cType
    return json.loads(rc)
