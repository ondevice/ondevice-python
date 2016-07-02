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

def getClient(name, devId, svcName, auth=None):
    mod = load(name)
    rc = mod.Client()
    rc._conn = Connection(devId, name, svcName, auth=auth, cb=rc.gotData)
    return rc

def getService(req, devId):
    mod = load(req.protocol)
    rc = mod.Service(req, devId)
    rc._conn = Response(req.broker, req.tunnelId, devId, cb=rc.gotData)
    return rc
