from core.connection import Connection, Response
from threading import Thread

class Endpoint:
    def startRemote(self):
        self._remoteThread = Thread(target = self.runRemote)
        self._remoteThread.start()

    def startLocal(self):
        self._localThread = Thread(target = self.runLocal)
        self._localThread.start()


    def runRemote(self):
        self._conn.run()


def load(name):
    mod = __import__('modules.{0}'.format(name))
    return getattr(mod, name)

def loadClass(name, className):
    modName, suffix = (name.split(':')+[None])[:2]
    if suffix != None:
        className = '{0}_{1}'.format(className, suffix)
    mod = load(modName)

    if not hasattr(mod, className):
        raise Exception("Module '{0}' doesn't have a '{1}' endpoint".format(modName, suffix))
    return getattr(mod, className)

def getClient(name, devId, svcName, auth=None):
    rc = loadClass(name, 'Client')()
    rc._conn = Connection(devId, name, svcName, auth=auth, cb=rc.gotData)
    return rc

def getService(req, devId):
    mod = load(req.protocol)
    rc = mod.Service(req, devId)
    rc._conn = Response(req.broker, req.tunnelId, devId, cb=rc.gotData)
    return rc
