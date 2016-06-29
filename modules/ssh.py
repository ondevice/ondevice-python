
def onConnect(request):
    print ("got incoming SSH connection request: {0}".format(request))
    return SshConnection(request)

class SshConnection:
    def __init__(self, request):
        self.request = request
