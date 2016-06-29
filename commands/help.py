"""
Lists available commands or prints detailed help for one of them

Examples:
    {cmd} help          lists available commands
    {cmd} help listen   shows the help for the 'listen' command
    {cmd} help help     shows this message
"""

import commands
import sys

def run(cmdName=None):
    if cmdName == None:
        print("USAGE: {0} <command> [args]\n".format(sys.argv[0]))
        print("Commands:")

        for cmd in commands.listCommands():
            args, msg = commands.usage(cmd)
            print("\t{0} {1}\n\t\t{2}".format(cmd, args, msg))
    else:
        cmd = commands.load(cmdName)
        args, msg = cmd.usage()
        print('{0} {1} {2}'.format(sys.argv[0], cmdName, args))
        print(cmd.__doc__.format(cmd=sys.argv[0]))

def usage():
    return "[cmd]", "lists available commands or prints detailed help for one"
