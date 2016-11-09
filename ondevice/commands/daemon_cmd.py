"""
Run the ondevice daemon.

Options:

-f
--foreground
    Don't run as background daemon but keep attached to the terminal

"""

usage = {
    'msg': 'Run the ondevice device daemon',
    'group': 'device'
}

from ondevice.core import config, daemon, exception
from ondevice import control

from daemon import DaemonContext

import getopt

def runDaemon():
    control.server.start()
    daemon.runForever()
    control.server.start()

def run(*args):
    opts, args = getopt.gnu_getopt(args, 'C:f', ('configDir=', 'foreground'))
    foreground = False

    if len(args) > 0:
        raise exception.UsageError("Extra arguments: {0}".format(args))

    for k,v in opts:
        if k in ['-C', '--configDir']:
            config.configDir = v
            config.invalidateCache()

        elif k in ['-f', '--foreground']:
            foreground = True

    if foreground:
        runDaemon()
    else:
        with DaemonContext():
            runDaemon()
