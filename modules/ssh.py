from core.connection import Connection

class Client:
    def __init__(self, dev, svcName, auth=None):
        if auth == None:
            raise Exception("Missing auth key!")
        self._conn = Connection(dev, 'ssh', svcName, auth=auth, cb=self._gotData)

    def connect(self):
        self._conn.run()

    def _gotData(self, ws, data):
        print("-- got data: {0}".format(data))

class Service:
    def __init__(self, request):
        print ("got incoming SSH connection request: {0}".format(request))
        self._request = request
