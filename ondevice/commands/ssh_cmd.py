"""
Connect to your devices using the 'ssh' command.

Usage:
    ondevice ssh [<user>@]<device> [ssh-arguments...]

This is a relatively thin wrapper around the `ssh` command.
The main difference to invoking ssh directly is that instead of regular host names you'll have to specify an ondevice deviceId.
The connection is routed through the ondevice.io network.

ondevice ssh will try to parse ssh's arguments, the first non-argument has to be
the user@hostname combo.

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

from ondevice.core import tunnel

import getopt
import subprocess
import sys

usage = {
    'msg': 'Connect to your devices using the ssh protocol',
    'args': '[ssh-arguments...]',
    'group': 'client'
}

def run(*args):
    # option list copied from debian jessie's openssh source package (from ssh.c, line 509)
    opts, nonopts = getopt.getopt(args, '1246ab:c:e:fgi:kl:m:no:p:qstvx')
    nonopts = list(nonopts)

    devId = nonopts.pop(0)
    sshUser = None
    if '@' in devId:
        sshUser, devId = devId.split('@', 1)

    # prepare command
    cmd = ['ssh', '-oProxyCommand={0} connect ssh:tunnel {1}'.format(sys.argv[0], devId)]

    # add options
    for k,v in opts:
        cmd.append('{0}{1}'.format(k,v))

    # add hostname (and user) in the format user@ondevice:devUser.devId
    qualifiedId = tunnel.qualifyDeviceId(devId)
    hostname = 'ondevice:{0}'.format(qualifiedId)
    if sshUser != None:
        hostname = '{0}@{1}'.format(sshUser, hostname)
    cmd.append(hostname)

    ssh = subprocess.Popen(cmd + nonopts, stdin=None, stdout=None, stderr=None)
    return ssh.wait()
