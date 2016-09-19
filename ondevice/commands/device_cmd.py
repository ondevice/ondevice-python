"""Manage device properties

- {cmd} device <devName> props <devName> [key]... - List a device's properties
- {cmd} device <devName> set <devName> <key>=<value>... - set one or more device properties
- {cmd} device <devName> rm <key>... - remove specific device properties

Examples:
$ {cmd} device someDevice props
foo=bar
abc=123

$ {cmd} device someDevice props foo hello
foo=bar
hello=

$ {cmd} device someDevice rm abc
foo=bar

$ {cmd} device someDevice set hello=world answer=42
foo=bar
hello=world
answer=42
"""

usage = {
    'args': '<devName> props/set/rm [args]',
    'msg': "Fetch/Manage a device's information",
    'group': 'client'
}


from ondevice.core import exception, rest, sock


def _printProps(resp):
    for devId, devProps in resp['props'].items():
        for key,value in devProps.items():
            print("{0}={1}".format(key,value))


def propList(devName, *keys):
    resp = rest.apiGET("/device/{0}/props".format(devName))
    _printProps(resp)

def propSet(devName, *values):
    props = {}
    for val in values:
        k,v = val.split('=')
        props[k] = v

    resp = rest.apiPOST("/device/{0}/props".format(devName), data={'props': props})
    _printProps(resp)

def propRm(devName, *keys):
    resp = rest.apiDELETE("/device/{0}/props".format(devName), data={'props': keys})
    _printProps(resp)

def run(devName, subcmd, *args):
    if subcmd == 'props':
        propList(devName, *args)
    elif subcmd == 'set':
        propSet(devName, *args)
    elif subcmd == 'rm':
        propRm(devName, *args)
    else:
        raise exception.UsageError("Unsupported subcommand: {0}".format(subcmd))
