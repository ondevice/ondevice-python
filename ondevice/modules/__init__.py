from ondevice.core.connection import Connection, Response

import io
import re
from threading import Thread

class Endpoint:
    def getConsoleBuffer(self, stream):
        """ Compatibilty code for py2/3 (returns stream.buffer in py3 and io.BufferedReader/BufferedWriter in py2) """
        if hasattr(stream, 'buffer'):
            return stream.buffer # py3
        else:
            rc = io.open(stream.fileno()) # py2
            if hasattr(rc, 'read'):
                rc.read1 = rc.read # this is hacky but it seems to work
            return rc

    def startRemote(self):
        self._remoteThread = Thread(target = self.runRemote)
        self._remoteThread.start()

    def startLocal(self):
        self._localThread = Thread(target = self.runLocal)
        self._localThread.start()

    def gotData(self, data):
        raise Exception("This module doesn't impolement the 'gotData' endpoint!?!")

    def runRemote(self):
        self._conn.run()

class TunnelClient(Endpoint):
    def __init__(self, devId, protocol, svcName, *args, auth=None):
        if len(args) > 0:
            raise Exception("Too many arguments!")

        self._params = { 'devId': devId, 'svcName': svcName }
        if auth != None:
            self._params['auth'] = auth

        self._conn = Connection(devId, protocol, svcName, auth=auth, cb=self.gotData)

class TunnelService(Endpoint):
    def __init__(self, brokerUrl, tunnelId, devId):
        self._conn = Response(brokerUrl, tunnelId, devId, cb=self.gotData)


def load(name):
    ondevice = __import__('ondevice.modules.{0}'.format(name))
    return getattr(ondevice.modules, name)

def loadClient(devId, protocolStr, *args, auth=None):
    modName, suffix, svcName = _parseProtocolString(protocolStr)
    if svcName == None:
        svcName = modName
    return loadClient2(devId, modName, suffix, svcName, *args, auth=auth)

def loadClient2(devId, modName, suffix, svcName, *args, auth=None):
    className = 'Client'

    if suffix != None:
        className = '{0}_{1}'.format('Client', suffix)
    mod = load(modName)

    if not hasattr(mod, className):
        raise Exception("Module '{0}' doesn't have a '{1}' endpoint".format(modName, suffix))
    clazz = getattr(mod, className)
    rc = clazz(devId, modName, svcName, *args, auth=auth)
    rc._params.update({'protocol': modName, 'endpoint': suffix })
    return rc

def getService(req, devId):
    mod = load(req.protocol)
    rc = mod.Service(req.broker, req.tunnelId, devId)
    return rc

def _parseProtocolString(protocolStr):
    """ Takes a protocol string (in the format `moduleName[:suffix][@svcName]`)
    and returns its parts (or None for each missing part) """
    return re.match('([^:@]+):?([^@]+)?@?(.+)?', protocolStr).groups()
