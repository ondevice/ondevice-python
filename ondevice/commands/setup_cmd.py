"""
Set up the API keys for communicating with the ondevice.io service.

Example:
$ ondevice setup
User: ondevice
API key: **********
INFO:root:Updated client key (user: 'ondevice')
"""

usage = {
    'msg': 'Set up the API keys for communicating with the ondevice.io service'
}

from ondevice.core import config, rest, sock

import getpass
import logging
import six


def run():
    setupKeys()
    # TODO set up autostart

def setupKeys():
    # TODO check if the config file already has API keys (and ask if the user really wants to overwrite them)
    user,key = queryCredentials()

    config.overrides.put('client', 'user', user)
    config.overrides.put('client', 'auth', key)

    resp = rest.apiGET('/keyInfo')
    config.overrides.clear() # just to be sure, reset to default authentication

    roles = resp['roles']

    if 'client' in roles:
        config.setClientUser(user)
        config.setClientAuth(key)
        logging.info("Updated client key (user: '{0}')".format(user))
    if 'device' in roles:
        config.setDeviceUser(user)
        config.setDeviceAuth(key)
        logging.info("Updated device key (user: '{0}')".format(user))


def queryCredentials():
    user = six.moves.input('User: ')
    key = getpass.getpass('API key: ')
    return user,key
