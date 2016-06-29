import pkgutil

def listCommands():
    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        if not ispkg:
            yield modname

def load(cmdName):
    mod = __import__('commands.{0}'.format(cmdName))
    return getattr(mod, cmdName)

def run(cmdName, *args, **opts):
    cmd = load(cmdName)
    cmd.run(*args, **opts)

def usage(cmdName):
    cmd = load(cmdName)
    return cmd.usage()
