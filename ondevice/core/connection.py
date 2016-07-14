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
            return self._cb(messageData)
        elif msgType == b'meta':
            if messageData == b'connected':
                logging.debug("-- connected --")
                self._onConnected()
            elif messageData == b'EOF':
                logging.debug("-- got EOF --")
                self.onEOF()
            else:
                raise Exception("Unsupported meta message: '{0}'", messageData)
        elif msgType == b'error':
            code, messageData = self._takeHeader(messageData)
            code = int(code)
            self.onError(code, messageData.decode('utf8'))
        else:
            raise Exception("Unsupported message type: '{0}'".format(msgType))

    def _onConnected(self):
        self._lock.release()

    def _takeHeader(self, msg, default=None):
        colonPos = msg.find(b':')
        hdr = None
        if colonPos >= 0:
            hdr = msg[:colonPos]
            msg = msg[colonPos+1:]
        elif default != None:
            hdr = default
        else:
            raise Exception('missing header (msg: {0})'.format(msg))
        return hdr, msg

    def onEOF(self):
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
    def __init__(self, dev, protocol, service, cb=None, auth=None):
        self._cb = cb

        if auth != None:
            config.setClientAuth(auth)
        else:
            user,_ = parseDeviceName(dev)
            auth = config.getClientAuth(user)
            if auth == None:
                logging.error("Missing authentication key. You'll have to set it once using the --auth=... option")
                sys.exit(1)

        TunnelSocket.__init__(self, '/connect', auth=auth, dev=dev, protocol=protocol, service=service)


class Response(TunnelSocket):
    def __init__(self, broker, tunnelId, dev, cb=None):
        TunnelSocket.__init__(self, '/accept', tunnel=tunnelId, dev=dev, baseUrl=broker)
        self._cb = cb

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
