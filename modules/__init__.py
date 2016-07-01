
def load(name):
    mod = __import__('modules.{0}'.format(name))
    return getattr(mod, name)

def getClient(name, dev, svcName, auth=None):
    mod = load(name)
    return mod.Client(dev, svcName, auth=auth)

def getService(request, devId):
    mod = load(request.protocol)
    return mod.Service(request, devId)
