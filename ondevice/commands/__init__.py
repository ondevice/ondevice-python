import pkgutil

def listCommands():
    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        if not ispkg:
            yield modname

def load(cmdName):
    ondevice = __import__('ondevice.commands.{0}'.format(cmdName))
    return getattr(ondevice.commands, cmdName)

def run(cmdName, *args, **opts):
    cmd = load(cmdName)
    cmd.run(*args, **opts)

def usage(cmdName):
    cmd = load(cmdName)
    return cmd.usage()