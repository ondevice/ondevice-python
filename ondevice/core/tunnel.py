from ondevice.core import config, sock, thread, state

import logging
import threading
import time

class TunnelInfo:
    """ Contains information on a tunnel connection.
    Mandatory attributes:
    - service
    - protocol
    - devId/clientUser (depending on whether we're used on the client or device side)
    
    Optional attributes:
    - bytesSent
    - bytesReceived
    - clientUser """

    def __init__(self, **kwargs):
        # make sure we have at least the following arguments:
        for expectedKeys in 'devId/clientUser,service,protocol'.split(','):
            found = False
            for key in expectedKeys.split('/'):
                if key in kwargs:
                    found = True
                    break
                
            if not found:
                raise Exception("Missing TunnelInfo argument: '{0}' (only got: {1})".format(expectedKeys, kwargs.keys()))

        self.bytesSent = 0
        self.bytesReceived = 0
        self.connectedAt = time.time()

        # set the object attributes
        for k, v in kwargs.items():
            setattr(self, k, v)


class TunnelSocket(sock.Socket):
    """ Base class for Connection and Response. """
    def __init__(self, endpoint, info, auth, listener=None, **params):
        if listener != None:
            self.listener = listener
        self._eof = False
        self._lock = threading.Lock()
        self._lock.acquire() # lock initially (will be released once the server confirms the connection)
        self.lastPing = None
        self.info = info
        self.info.connId = state.add('tunnels', 'seq', 1)

        baseUrl = info.brokerUrl if hasattr(info, 'brokerUrl') else None
        sock.Socket.__init__(self, endpoint, auth, baseurl=baseUrl, **params)

        taskName = 'conn_{0}:ping'.format(info.connId)
        self._pingTask = thread.FixedDelayTask(self._ping, 60, name=taskName)

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
        self.info.bytesReceived += len(messageData)
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
            elif msgType == b'ping':
                logging.debug("-- got ping message --")
                self.lastPing = time.time()

                pongMsg = b'meta:pong'
                if messageData != None:
                    pongMsg += messageData
                self._ws.send(pongMsg, 2) #OPCODE_BINARY
            elif msgType == b'pong':
                self.lastPing = time.time()
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
        self._pingTask.start()

        if self._hasListener('onConnected'):
            self._callListener('onConnected')

    def _onClose(self, ws):
        self._pingTask.stop()
        # TODO we should probably relock self._lock here
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

    def _ping(self):
        """ check that the last ping has been received within the last five minutes.
        These checks will only start after at least one ping/pong was received.
        That way older versions of the ondevice client can coexist with newer ones."""
        if self.lastPing != None:
            now = time.time()
            logging.debug("last ping received: {0}s ago".format(now - self.lastPing))
            if now - self.lastPing > 300:
                self.onError(-1, 'Connection lost')
                self._ws.close()
                raise Exception("Connection timed out :(")

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

            self.info.bytesSent += len(data)
            self._ws.send(data, 2) # OPCODE_BINARY

    def sendEOF(self):
        with self._lock:
            logging.debug("-- Sending EOF --")
            self._ws.send(b'meta:EOF', 2) #OPCODE_BINARY

class Connection(TunnelSocket):
    def __init__(self, info, listener=None):
        user,dev = parseDeviceId(info.devId)
        auth = config.getClientAuth(user)

        if auth[0] == user:
            # device belongs to local user (or at least to a user we have credentials for) -> use the unqualified devId
            devId = dev
        else:
            devId = info.devId
            
        #def __init__(self, endpoint, info, auth, listener=None, **params):
        TunnelSocket.__init__(self, '/connect', info, auth=auth, listener=listener, dev=devId, protocol=info.protocol, service=info.service)

    def _ping(self):
        logging.debug('sending tunnel ping')
        self._ws.send(b'meta:ping', 2) #OPCODE_BINARY
        TunnelSocket._ping(self)

class Response(TunnelSocket):
    def __init__(self, info, listener=None):
        auth = (config.getDeviceUser(), config.getDeviceAuth())
        TunnelSocket.__init__(self, '/accept', info, auth=auth, listener=listener, tunnel=info.tunnelId, key=info.devKey)

    def onEOF(self):
        """ Got an EOF from the remote host -> closing the websocket """
        with self._lock:
            self._ws.close()

    def _onClose(self, ws):
        state.add('tunnels', 'count', -1)
        state.remove('tunnels', 'info', self.info.connId)
        return TunnelSocket._onClose(self, ws)

    def _onConnected(self):
        state.add('tunnels', 'count', 1)
        state.set('tunnels.info', self.info.connId, self.info.__dict__)
        return TunnelSocket._onConnected(self)


def qualifyDeviceId(name):
    '''prepends the user name to unqualified device IDs
        - name: Device name (e.g. dev1, user0.dev1)

        returns: qualified deviceID (e.g. user0.dev1)
            if the name parameter was already qualified, it's returned as is.
    '''

    if '.' in name:
        return name
    elif '/' in name: # legacy user/device format (replace with the dot format)
        return '.'.join(name.split('/', 1))
    else:
        return '.'.join([config.getClientUser(), name])

def parseDeviceId(devId):
    '''Splits a (possibly) qualified device ID into its components

        - name:  Device name (e.g. dev1, user0.dev1)

        returns: (userName, deviceId)
          if the userName is not part of the name parameter, config.getClientUser() is returned
    '''
    user = None

    if '.' in devId: # format: user.device
        user, devId = devId.split('.', 1)
    elif '/' in devId: # legacy device IDs
        user, devId = devId.split('/', 1)
    else:
        user = config.getClientUser()

    return user, devId
