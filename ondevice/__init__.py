#!/usr/bin/env python3

import logging
import pkg_resources
import os, sys

from ondevice import commands

def _main():
    return main(sys.argv[1:])

def main(args):
    logging.basicConfig(level=logging.INFO)

    if len(args) < 1:
        usage()
    else:
        opts = parseArgs(args)

        cmd = args.pop(0)
        if cmd.startswith(':'):
            args.insert(0, cmd[1:])
            cmd = 'connect'

        return commands.run(cmd, *args, **opts)

def getVersion():
    pkgInfo = pkg_resources.require("ondevice")[0]
    return pkgInfo.version


def parseArgs(args, aliases={}):
    """ takes all options (anything starting with a -- or a -) from `args`
    up until the first non-option.
    short options (those with only one dash) will be converted to their long
    version if there's a matching key in `shortOpts`. If there isn't, an
    KeyError is raised."""
    rc = {}

    while len(args) > 0 and args[0].startswith('-'):
        opt = args.pop(0)
        if opt == '--':
            break # ignore and exit

        # treat options with one dash the same as those with two dashes
        if opt.startswith('--'):
            opt = opt[2:]
        elif opt.startswith('-'):
            opt = opt[1:]

        equalsPos = opt.find('=')
        val = None
        if equalsPos >= 0:
            val = opt[equalsPos+1:]
            opt = opt[:equalsPos]

        rc[opt] = val

    return rc

def usage(exitCode=1):
    commands.run('help')
    sys.exit(exitCode)

if __name__ == '__main__':
    sys.exit(_main())
