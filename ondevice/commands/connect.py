"""
Attempts to initiate a connection to a device's service.

There is actually a shorthand. Instead of `ondevice connect <module> ...` you
can write:

    `ondevice :<module> ...`

Arguments:
- module:   The module to use for the connection (e.g. 'ssh')
- dev:      Device to connect to
- svcName:  Service name (defaults to the module name)

Examples:
    {cmd} connect ssh someDevice - connect to the 'ssh' service of 'someDevice'
    {cmd} :ssh someDevice - same as the above (i.e. omitted 'connect')
    {cmd} :ssh@otherSsh someDevice - connect to the 'otherSsh' service using ssh
"""

usage = {
    'args': '<module> <dev> [svcName]',
    'msg': 'Connects to a service on the specified device (shorthand: `:<module>`)',
    'group': 'client'
}

from ondevice import modules


def run(module, dev, *args):
    client = modules.loadClient(devId=dev, protocolStr=module, args=args)
    client.startRemote()

    args = ()
    if hasattr(client, '_args'): args = client._args
    client.runLocal(*args) # don't run in a background thread
