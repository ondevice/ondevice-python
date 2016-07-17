from ondevice.core import config, sock

import logging
import threading
import sys

class TunnelSocket(sock.Socket):
    """ Base class for Connection and Response """
    def __init__(self, *args, **kwargs):
        self._lock = threading.Lock()
        self._lock.acquire() # lock initially (will be released once the server confirms the connection)
        sock.Socket.__init__(self, *args, **kwargs)

    def _onMessage(self, ws, messageData):
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
            return self._messageCB(messageData)
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
        if hasattr(self, '_eofCB'):
            self._eofCB()
        else:
            raise Exception("No one implemented EOF!?!")

    def onError(self, code, msg):
        raise Exception("Error (code={0}): {1}".format(code, msg))

    def send(self, msg):
        if (type(msg) != bytes):
            raise Exception("expected bytes, not {0}".format(type(msg)))

        with self._lock:
            logging.debug('{0} >> {1} ({2} bytes)'.format('data', msg, len(msg)))
            data = b'data:'+msg

            self._ws.send(data, 2) # OPCODE_BINARY

    def sendEOF(self):
        with self._lock:
            logging.info("-- Sending EOF --")
            self._ws.send(b'meta:EOF', 2) #OPCODE_BINARY

class Connection(TunnelSocket):
    def __init__(self, dev, protocol, service, onMessage=None, onEOF=None):
        self._messageCB = onMessage
        self._eofCB = onEOF

        user,dev = parseDeviceName(dev)
        auth = config.getClientAuth(user)
        TunnelSocket.__init__(self, '/connect', auth=auth, dev=dev, protocol=protocol, service=service)


class Response(TunnelSocket):
    def __init__(self, broker, tunnelId, dev, onMessage=None):
        auth = (config.getDeviceUser(), config.getDeviceAuth())
        TunnelSocket.__init__(self, '/accept', tunnel=tunnelId, dev=dev, baseUrl=broker, auth=auth)
        self._messageCB = onMessage

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
