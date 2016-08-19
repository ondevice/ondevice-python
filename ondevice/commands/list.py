"""
Prints detailed information on your devices

Examples:
$ {cmd} list
ID          State               IP          Version     Name
foo/dev1    OFFLINE (for 1h)    1.2.3.4     0.1dev6     Device 1
foo/raspi   ONLINE (for 2d)     1.2.3.5     0.1dev6     Raspberry PI at home
"""

usage = {
    'msg': 'Displays detailed information on your devices',
    'group': 'client'
}

from ondevice.core import rest, sock

import json


def run(*args):
    resp = rest.apiGET('/devices')

    # TODO do proper option parsing
    # TODO support '--state=on/offline' option
    if '--json' in args:
        for dev in resp['devices']:
            print(json.dumps(dev))
#    elif '--raw' in args:
#        print(json.dumps(resp))
    else:
        fmt='{id:20s} {state:10s} {ip:15s} {version:10s} {name}'
        print(fmt.format(id='ID',state='State', ip='IP', version='Version', name='Name'))

        for dev in resp['devices']:
            if not 'name' in dev:
                dev['name'] = ''
            print(fmt.format(**dev))
