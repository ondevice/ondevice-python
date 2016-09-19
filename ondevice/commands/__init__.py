from ondevice.core import exception

import pkgutil

def listCommands():
    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        if not ispkg and modname.endswith('_cmd'):
            yield modname[:-4]

def load(cmdName):
    try:
        ondevice = __import__('ondevice.commands.{0}_cmd'.format(cmdName))
    except ImportError:
        raise exception.UsageError("Unknown command, try 'ondevice help' for a list of commands: {0}".format(cmdName))
    return getattr(ondevice.commands, '{0}_cmd'.format(cmdName))

def run(cmdName, *args, **opts):
    cmd = load(cmdName)
    return cmd.run(*args, **opts)

def usage(cmdName):
    cmd = load(cmdName)
    if not hasattr(cmd, 'usage'):
        raise exception.ImplementationError("Command '{0}' doesn't have 'usage' information".format(cmdName))
    if callable(cmd.usage):
        args, msg = cmd.usage()
        return {'args': args, 'msg': msg}
    else: return cmd.usage
