"""Manage device properties

- {cmd} prop list <devName> [key]... - List a device's properties
- {cmd} prop set <devName> <key>=<value>... - set one or more device properties
- {cmd} prop rm <devName> <key>... - remove specific device properties

Examples:
$ {cmd} prop list me/someDevice
foo=bar
abc=123

$ {cmd} prop list me/someDevice foo hello
foo=bar
hello=

$ {cmd} prop rm me/someDevice abc
foo=bar

$ {cmd} prop set me/someDevice hello=world answer=42
foo=bar
hello=world
answer=42
"""

from ondevice.core import sock


def _printProps(resp):
    for devId, devProps in resp['props'].items():
        for key,value in devProps.items():
            print("{0}={1}".format(key,value))


def propList(devName, *keys):
    resp = sock.apiGET("/device/{0}/props".format(devName))
    _printProps(resp)

def propSet(devName, *values):
    props = {}
    for val in values:
        k,v = val.split('=')
        props[k] = v

    resp = sock.apiPOST("/device/{0}/props".format(devName), data={'props': props})
    _printProps(resp)

def propRm(devName, *keys):
    resp = sock.apiDELETE("/device/{0}/props".format(devName), data={'props': keys})

def run(subcmd, devName, *args):
    if subcmd == 'list':
        propList(devName, *args)
    elif subcmd == 'set':
        propSet(devName, *args)
    elif subcmd == 'rm':
        propRm(devName, *args)
    else:
        raise Exception("Unsupported subcommand: {0}".format(subcmd))

def usage():
    return "list/set/rm <devName> [args]", "Manage device properties"
