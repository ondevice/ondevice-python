from ondevice.core.connection import Connection, Response

from threading import Thread

class Endpoint:
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


def load(name):
    ondevice = __import__('ondevice.modules.{0}'.format(name))
    return getattr(ondevice.modules, name)

def loadClient(name):
    modName, suffix = (name.split(':')+[None])[:2]
    className = 'Client'

    if suffix != None:
        className = '{0}_{1}'.format('Client', suffix)
    mod = load(modName)

    if not hasattr(mod, className):
        raise Exception("Module '{0}' doesn't have a '{1}' endpoint".format(modName, suffix))
    rc = getattr(mod, className)()
    rc._params = {'protocol': modName, 'endpoint': suffix }
    return rc, modName


def getClient(name, devId, svcName, auth=None):
    rc, name  = loadClient(name)

    rc._params.update({ 'devId': devId, 'svcName': svcName })
    if auth != None:
        rc._params['auth'] = auth

    rc._conn = Connection(devId, name, svcName, auth=auth, cb=rc.gotData)
    return rc

def getService(req, devId):
    mod = load(req.protocol)
    rc = mod.Service(req, devId)
    rc._conn = Response(req.broker, req.tunnelId, devId, cb=rc.gotData)
    return rc
