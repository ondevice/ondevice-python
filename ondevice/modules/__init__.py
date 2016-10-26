from ondevice.core import config, exception, service, thread
from ondevice.core.tunnel import Connection, Response, TunnelInfo

import imp
import io
import logging
import os
import pkgutil
import re

class Endpoint:
    def __init__(self, info):
        self.info = info

    def getConsoleBuffer(self, stream):
        """ Compatibilty code for py2/3 (returns stream.buffer in py3 and io.BufferedReader/BufferedWriter in py2) """
        if hasattr(stream, 'buffer'):
            return stream.buffer # py3
        else:
            mode = stream.mode
            if mode in ['r','w']:
                mode = mode+'b'
            elif mode in ['rb','wb']:
                pass
            else:
                raise exception.ImplementationError("Unexpected stream mode: {0}".format(mode))

            rc = io.open(stream.fileno(), mode=mode) # py2
            if hasattr(rc, 'read'):
                rc.read1 = rc.read # this is hacky but it seems to work
            return rc

    def startRemote(self):
        threadName = 'conn_{0}:remote'.format(self.info.connId)
        self._remoteThread = thread.BackgroundThread(self.runRemote, self.stopRemote, name=threadName)
        self._remoteThread.start()

    def startLocal(self):
        threadName = 'conn_{0}:local'.format(self.info.connId)
        args = self._args if hasattr(self, '_args') else ()

        self._localThread = thread.BackgroundThread(self.runLocal, self.stopLocal, name=threadName, args=args)
        self._localThread.start()

    def onMessage(self, data):
        raise exception.ImplementationError("This module doesn't implement the 'onMessage' method!?!")

    def runRemote(self):
        self._conn.run()

    def stopRemote(self):
        """ Closes the tunnel connection """
        self._conn.close()

class ModuleClient(Endpoint):
    def __init__(self, info, args):
        Endpoint.__init__(self, info)
        self._args = args
        self._conn = Connection(info, listener=self)

    def onClose(self):
        raise exception.ImplementationError("onClose not implemented!")

    def onEOF(self):
        raise exception.ImplementationError("onEOF not implemented!")

class ModuleService(Endpoint):
    def __init__(self, info):
        Endpoint.__init__(self, info)
        self._conn = Response(info, listener=self)

    def onClose(self):
        logging.info("Tunnel closed (bytes sent=%d, received=%d)", self.info.bytesSent, self.info.bytesReceived)

def exists(name):
    return name in listModules()

def listModules():
    knownNames = []
    for importer, modName, isPkg in pkgutil.iter_modules(__path__):
        if not isPkg:
            knownNames.append(modName)
            yield modName

    # list user-local modules (stored in .config/ondevice/modules)
    userPath = config._getConfigPath('modules')
    for importer, modName, isPkg in pkgutil.iter_modules([userPath]):
        if not isPkg and modName not in knownNames:
            yield modName

def load(name):
    try:
        ondevice = __import__('ondevice.modules.{0}'.format(name))
        return getattr(ondevice.modules, name)
    except ImportError as e:
        # maybe there's a user-installed module?
        # TODO use importlib if possible
        userPath = config._getConfigPath('modules')
        mod = imp.load_source('usermodules.{0}'.format(name), os.path.join(userPath, '{0}.py'.format(name)))
        return mod

def loadClient(devId, protocolStr, args):
    modName, suffix, svcName = _parseProtocolString(protocolStr)
    if svcName == None:
        svcName = modName
    return loadClient2(devId=devId, modName=modName, suffix=suffix, svcName=svcName, args=args)

def loadClient2(devId, modName, suffix, svcName, args):
    className = 'Client'

    if suffix != None:
        className = '{0}_{1}'.format('Client', suffix)
    mod = load(modName)

    if not hasattr(mod, className):
        raise exception.UsageError("Module '{0}' doesn't have a '{1}' endpoint".format(modName, suffix))
    clazz = getattr(mod, className)
    info=TunnelInfo(devId=devId, protocol=modName, service=svcName, clientUser=config.getClientUser())
    rc = clazz(info, args=args)
    return rc

def getService(req, devKey):
    svc = service.get(req.service)
    if svc['protocol'] != req.protocol:
        raise Exception("Error: protocol mismatch (expected={0}, actual={1})".format(svc['protocol'], req.protocol))
    mod = load(req.protocol)
    info = TunnelInfo(devKey=devKey, tunnelId=req.tunnelId, brokerUrl=req.broker,
            service=req.service, protocol=req.protocol, clientUser=req.clientUser)
    rc = mod.Service(info)
    return rc

def _parseProtocolString(protocolStr):
    """ Takes a protocol string (in the format `moduleName[:suffix][@svcName]`)
    and returns its parts (or None for each missing part) """
    return re.match('([^:@]+):?([^@]+)?@?(.+)?', protocolStr).groups()
