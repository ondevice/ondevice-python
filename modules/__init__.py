
def load(name):
    mod = __import__('modules.{0}'.format(cmdName))
    return getattr(mod, cmdName)
