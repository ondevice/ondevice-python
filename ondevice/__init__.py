#!/usr/bin/env python3

import logging
import pkg_resources
import os, sys

from ondevice import commands

def _main():
    main(sys.argv[1:])

def main(args):
    logging.basicConfig(level=logging.INFO)

    if len(args) < 1:
        usage()
    else:
        cmd = args.pop(0)
        if cmd.startswith(':'):
            args.insert(0, cmd[1:])
            cmd = 'connect'

        args, opts = parseArgs(args)
        commands.run(cmd, *args, **opts)

def getVersion():
    pkgInfo = pkg_resources.require("ondevice")[0]
    return pkgInfo.version


def parseArgs(inArgs):
    # to my knowledge it's not possible to use the getopt module if the names of the arguments aren't known in advance
    # please correct me if I'm wrong
    args = []
    opts = {}

    for a in inArgs:
        equalsPos = a.find('=')
        if equalsPos >= 0:
            opts[a[:equalsPos]] = a[equalsPos+1:]
        else:
            args.append(a)

    return args, opts

def usage(exitCode=1):
    commands.run('help')
    sys.exit(exitCode)

if __name__ == '__main__':
    _main()
