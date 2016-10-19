"""
Copy files from/to devices using rsync

Usage:

ondevice rsync [rsync-options...]

Examples:

- ondevice rsync -av /source/path/ root@myDev:/target/path/
    copy the local /src/path to myDev's /target/path/ as root
    (and pass the -a and -v options to rsync)
- ondevice rsync me@otherDev:/etc/motd /tmp/other.motd
    copy otherDev's /etc/motd file to /tmp/other.motd (and login as 'me')

This command is only a thin wrapper around the `rsync` client (using its `-e`
argument to make it use `ondevice ssh` internally).

"""

import subprocess
import sys

usage = {
    'msg': 'Copy files from/to your devices using rsync',
    'args': '[ssh-arguments...]',
    'group': 'client'
}

def run(*args):
    rsync = subprocess.Popen(['rsync', '-e', 'ondevice ssh'] + list(args), stdin=None, stdout=None, stderr=None)
    return rsync.wait()
