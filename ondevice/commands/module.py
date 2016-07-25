"""
{cmd} module [list]
    list the modules that are currently available.

{cmd} module info <name>

Modules have a device- and a client side implementation and essentially tunnel a
data in certain protocol through the ondevice.io network.
"""

# TODO enable this part of the documentation once user-installed modules are implemented
#There are a couple of modules already distributed with ondevice, but you can write
#your own and place them in ~/.config/ondevice/modules/ (of the user that runs
#ondevice)
#"""

usage = {
    'msg': 'Lists installed modules'
}

from ondevice import modules

import sys


def moduleInfo(name):
    mod = modules.load(name)
    print(mod.__doc__)


def listModules():
    for name in modules.listModules():
        mod = modules.load(name)
        info = '-- missing module information! --'
        if hasattr(mod, 'info'):
            info = mod.info
        print("{0}\t{1}".format(name, info))


def run(subcmd='list', *args):
    if subcmd == 'info':
        return moduleInfo(*args)
    elif subcmd == 'list':
        return listModules(*args)
    else:
        raise Exception("Unknown subcommand: {0}".format(subcmd))
