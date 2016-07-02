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
    {cmd} ssh someDevice otherSsh - connect to the 'otherSsh' service
"""

import modules

from core.session import Session

def run(module, dev, svcName=None, __sentinel__=None, auth=None):
    if __sentinel__ != None:
        raise Exception("Too many arguments")
    if svcName == None:
        svcName = module

    client = modules.getClient(module, dev, svcName, auth=auth)
    client.startRemote()
    client.runLocal() # don't run in a background thread

def usage():
    return "<module> <dev> [svcName]", "Connects to a service on the specified device"
