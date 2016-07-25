"""
Lists available commands or prints detailed help for one of them

Examples:
    {cmd} help          lists available commands
    {cmd} help listen   shows the help for the 'listen' command
    {cmd} help help     shows this message
"""

usage = {
    'args': '[cmd]',
    'msg': 'lists available commands or prints detailed help for one'
}

from ondevice import commands

import sys

def run(cmdName=None):
    if cmdName == None:
        print("USAGE: {0} <command> [args]\n".format(sys.argv[0]))
        print("Commands:")

        for cmd in commands.listCommands():
            usage = commands.usage(cmd)
            usage.setdefault('cmd', cmd)
            usage.setdefault('args', '')
            print("\t{cmd} {args}\n\t\t{msg}".format(**usage))
    else:
        cmd = commands.load(cmdName)
        usage = commands.usage(cmdName)
        usage.setdefault('cmd', cmdName)
        usage.setdefault('args', '')
        print('{0} {cmd} {args}'.format(sys.argv[0], **usage))
        print(cmd.__doc__.format(cmd=sys.argv[0]))
