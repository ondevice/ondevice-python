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

from ondevice.core import config, sock

import getpass
import logging
import six


def run():
    setupKeys()
    # TODO set up autostart

def setupKeys():
    # TODO check if the config file already has API keys (and ask if the user really wants to overwrite them)
    user,key = queryCredentials()

    resp = sock.apiPOST('/register', data={'user': user, 'key':key})
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
