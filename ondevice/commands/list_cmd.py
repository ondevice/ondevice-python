"""
Queries the ondevice.io server for details on all your devices

Arguments:
--json
    Print each host's details as json objects, one host per line
--props (only in conjunction with --json)
    Also include device properties in the JSON output

Examples:
$ {cmd} list
ID          State               IP          Version     Title
foo.dev1    OFFLINE (for 1h)    1.2.3.4     0.1dev6     Device 1
foo.raspi   ONLINE (for 2d)     1.2.3.5     0.1dev6     Raspberry PI at home

$ {cmd} list --json --props
{{"stateTs": 1474530839829, "version": "ondevice v0.2.4", "state": "online", "id": "foo.raspi", "props": {{"hello": "world"}}, "name": "Raspberry PI"}}
{{"stateTs": 1474472379545, "version": "0.2.1", "state": "online", "id": "foo.otherDev", "props": {{}}, "name": "NAS"}}
"""

usage = {
    'msg': 'Displays detailed information on your devices',
    'group': 'client'
}

from ondevice.core import exception, rest, sock

import json
import getopt


def run(*args):
    # TODO add '--state=on/offline' option
    optlist, args = getopt.gnu_getopt(args, '', ['json', 'props'])
    optlist = dict(optlist)
    restUrl = '/devices'

    if len(args) > 0:
        raise exception.UsageError('Unsupported commandline arguments: {0}'.format(args))

    if '--props' in optlist:
        restUrl = '/devices?props=true'
    resp = rest.apiGET(restUrl)

    if '--json' in optlist:
        for dev in resp['devices']:
            print(json.dumps(dev))
#    elif '--raw' in args:
#        print(json.dumps(resp))
    else:
        fmt='{id:20s} {state:10s} {ip:15s} {version:15s} {name}'
        print(fmt.format(id='ID',state='State', ip='IP', version='Version', name='Title'))

        for dev in resp['devices']:
            if not 'name' in dev:
                dev['name'] = ''
            print(fmt.format(**dev))
