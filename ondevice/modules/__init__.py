from ondevice.core import config, service
from ondevice.core.connection import Connection, Response

import imp
import io
import os
import pkgutil
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
        args = ()
        if hasattr(self, '_args'): args = self._args
        self._localThread = Thread(target = self.runLocal, args=args)
        self._localThread.start()

    def gotData(self, data):
        raise Exception("This module doesn't impolement the 'gotData' endpoint!?!")

    def runRemote(self):
        self._conn.run()

class TunnelClient(Endpoint):
    def __init__(self, devId, protocol, svcName, *args, auth=None):
        self._args = args

        self._params = { 'devId': devId, 'svcName': svcName }
        if auth != None:
            self._params['auth'] = auth

        self._conn = Connection(devId, protocol, svcName, auth=auth, cb=self.gotData)

class TunnelService(Endpoint):
    def __init__(self, brokerUrl, tunnelId, devId):
        self._conn = Response(brokerUrl, tunnelId, devId, cb=self.gotData)

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
    svc = service.get(req.service)
    if svc['protocol'] != req.protocol:
        raise Exception("Error: protocol mismatch (expected={0}, actual={1})".format(svc['protocol'], req.protocol))
    mod = load(req.protocol)
    rc = mod.Service(req.broker, req.tunnelId, devId)
    return rc

def _parseProtocolString(protocolStr):
    """ Takes a protocol string (in the format `moduleName[:suffix][@svcName]`)
    and returns its parts (or None for each missing part) """
    return re.match('([^:@]+):?([^@]+)?@?(.+)?', protocolStr).groups()
