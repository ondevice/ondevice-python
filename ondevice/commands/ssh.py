"""
Connect to your devices using the 'ssh' command.

Usage:
    ondevice ssh [<user>@]<device> [ssh-arguments...]

This is a relatively thin wrapper around the `ssh` command.
The main difference to invoking ssh directly is that instead of regular host names you'll have to specify an ondevice deviceId.
The connection is routed through the ondevice.io network.

Note that the user@device part has to be the first argument (all arguments
following it will be passed to ssh).

See ssh's documentation for further details.

Examples:
- ondevice ssh device1
    simply connect to device1
- ondevice ssh user@device1
    open an SSH connection to device1, logging in as 'user'
- ondevice ssh device1 echo hello world
    run 'echo hello world' on device1
- ondevice ssh device1 -N -L 1234:localhost:80
    Tunnel the HTTP server on device1 to the local port 1234 without opening
    a shell
- ondevice ssh device1 -D 1080
    Starting a SOCKS5 proxy listening on port 1080. It'll redirect all traffic
    to the target host.

"""

from ondevice.core import connection

import subprocess
import sys

usage = {
    'msg': 'Connect to your devices using the ssh protocol',
    'args': '[<user>@]<device> [ssh-arguments...]',
    'group': 'client'
}

def run(target, *args):
    if '@' in target:
        sshUser, devId = target.split('@', 1)
    else:
        sshUser = None
        devId = target


    proxyCmd = 'ProxyCommand={0} connect ssh:tunnel {1}'.format(sys.argv[0], devId)
    if sshUser != None:
        args = ['-l', sshUser]+list(args)

    # this prevents multiple known_hosts entries per device (a unqualified and a qualified one)
    qualifiedId = connection.qualifyDeviceId(devId)

    ssh = subprocess.Popen(['ssh', '-o', proxyCmd, 'ondevice:{0}'.format(qualifiedId)]+list(args), stdin=None, stdout=None, stderr=None)
    return ssh.wait()
