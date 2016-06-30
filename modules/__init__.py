
def load(name):
    mod = __import__('modules.{0}'.format(name))
    return getattr(mod, name)
