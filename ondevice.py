#!/usr/bin/env python3

import os, sys
import commands

def main(args):
    if len(args) < 1:
        usage()
    else:
        cmd = args.pop(0)
        commands.run(cmd, *args)

def usage(exitCode=1):
    commands.run('help')
    sys.exit(exitCode)

if __name__ == '__main__':
    main(sys.argv[1:])
