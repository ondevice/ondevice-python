"""
Attempts to initiate a connection to a device's service.

This is actually the default command (if 'module' is a known module), so you can
skip it if you want to.

Arguments:
- module:   The module to use for the connection (e.g. 'ssh')
- dev:      Device to connect to
- svcName:  Service name (defaults to the module name)

Examples:
    {cmd} connect ssh someDevice - connect to the 'ssh' service of 'someDevice'
    {cmd} ssh someDevice - same as the above (i.e. omitted 'connect')
    {cmd} ssh@otherSsh someDevice - connect to the 'otherSsh' service using ssh
"""

from ondevice import modules


def run(module, dev, auth=None, *args):
    client = modules.loadClient(devId=dev, protocolStr=module, *args)
    client.startRemote()

    args = ()
    if hasattr(client, '_args'): args = client._args
    client.runLocal(*args) # don't run in a background thread

def usage():
    return "<module> <dev> [svcName]", "Connects to a service on the specified device"
