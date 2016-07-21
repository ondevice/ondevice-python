from ondevice.core import config, sock

import logging
import threading
import sys

class TunnelSocket(sock.Socket):
    """ Base class for Connection and Response """
    def __init__(self, *args, **kwargs):
        if 'listener' in kwargs:
            self.listener = kwargs.pop('listener')
        self._eof = False
        self._lock = threading.Lock()
        self._lock.acquire() # lock initially (will be released once the server confirms the connection)
        self.bytesReceived = 0
        self.bytesSent = 0
        sock.Socket.__init__(self, *args, **kwargs)

    def _callListener(self, method, *args, **kwargs):
        if self.listener != None:
            if hasattr(self.listener, method):
                getattr(self.listener, method)(*args, **kwargs)
            else:
                raise Exception("missing callback: {0}".format(method))

    def _hasListener(self, method):
        return (self.listener != None
            and hasattr(self.listener, method)
            and callable(getattr(self.listener, method)))

    def _onMessage(self, ws, messageData):
        self.bytesReceived += len(messageData)
        colonPos = messageData.find(b':')
        if colonPos < 0:
            raise Exception('Missing message header')

        # 'header' examples:
        # - 'data:': data, channel 0
        # - 'data.3:': data, channel 3
        # - 'meta': metadata
        msgType, messageData = self._takeHeader(messageData)
        logging.debug('{0} << {1} ({2} bytes)'.format(msgType, repr(messageData), len(messageData)))

        if msgType == b'data':
            return self._callListener('onMessage', messageData)
        elif msgType == b'meta':
            msgType, messageData = self._takeHeader(messageData)

            if msgType == b'connected':
                if messageData != None:
                    params = self._parseParams(messageData)
                    assert b'api' in params
                else:
                    params = {b'api': b'v1.0'}

                logging.debug("-- connected --")
                self._apiVersion = params[b'api']
                self._onConnected()
            elif msgType == b'EOF':
                logging.debug("-- got EOF --")
                self.onEOF()
            else:
                raise Exception("Unsupported meta message: '{0}'".format(messageData))
        elif msgType == b'error':
            code, messageData = self._takeHeader(messageData)
            code = int(code)
            self.onError(code, messageData.decode('utf8'))
        else:
            raise Exception("Unsupported message type: '{0}'".format(msgType))

    def _onConnected(self):
        self._lock.release()
        if self._hasListener('onConnected'):
            self._callListener('onConnected')

    def _onClose(self, ws):
        if not self._eof:
            self.onEOF()
        if self._hasListener('onClose'):
            self._callListener('onClose')
        else:
            sock.Socket._onClose(self, ws)

    def _parseParams(self, params):
        """ Parse parameters in the format 'par1=val1,par2=val2' """
        rc = {}
        for param in params.split(b','):
            k,v = param.split(b'=')
            rc[k] = v
        return rc

    def _takeHeader(self, msg):
        colonPos = msg.find(b':')
        hdr = None
        if colonPos >= 0:
            hdr = msg[:colonPos]
            msg = msg[colonPos+1:]
        else:
            hdr = msg
            msg = None
        return hdr, msg

    def onEOF(self):
        if self._eof == False:
            self._eof = True
            self._callListener('onEOF')

    def onError(self, code, msg):
        if self._hasListener('onError'):
            self._callListener('onError', code, msg)
        else:
            raise Exception("Error (code={0}): {1}".format(code, msg))

    def send(self, msg):
        if (type(msg) != bytes):
            raise Exception("expected bytes, not {0}".format(type(msg)))

        with self._lock:
            logging.debug('{0} >> {1} ({2} bytes)'.format('data', msg, len(msg)))
            data = b'data:'+msg

            self.bytesSent += len(data)
            self._ws.send(data, 2) # OPCODE_BINARY

    def sendEOF(self):
        with self._lock:
            logging.info("-- Sending EOF --")
            self._ws.send(b'meta:EOF', 2) #OPCODE_BINARY

class Connection(TunnelSocket):
    def __init__(self, dev, protocol, service, listener=None):
        user,dev = parseDeviceName(dev)
        auth = config.getClientAuth(user)
        TunnelSocket.__init__(self, '/connect', auth=auth, dev=dev, protocol=protocol, service=service, listener=listener)


class Response(TunnelSocket):
    def __init__(self, broker, tunnelId, dev, listener=None):
        auth = (config.getDeviceUser(), config.getDeviceAuth())
        TunnelSocket.__init__(self, '/accept', tunnel=tunnelId, dev=dev, baseUrl=broker, listener=listener, auth=auth)

    def onEOF(self):
        """ Got an EOF from the remote host -> closing the websocket """
        with self._lock:
            self._ws.close()


def parseDeviceName(name):
    slashPos = name.find('/')
    user = None
    if slashPos >= 0:
        user = name[:slashPos]
        name = name[slashPos+1:]
    return user, name
