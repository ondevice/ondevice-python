
# TODO implement proper service handling (persisting the active services and giving the user a way to register/remove them easily)

from ondevice.core import config
from ondevice import modules

import json
import re

def add(name, protocol, hidden=False, **options):
    data = options
    data['protocol'] = protocol
    if hidden == True:
        data['hidden'] = True

    if not re.match('[a-zA-Z0-9_]+', name):
        raise Exception("Illegal characters in service name: '{0}'".format(name))

    if config.hasValue('services', name):
        raise Exception("Service '{0}' already exists!".format(name))
    # TODO have some nicer error messages
    modules.load(protocol)

    config.setValue('services', name, json.dumps(data))

def get(name):
    return listServices()[name]

def listServices():
    rc = {}
    for svcName in config.listKeys('services'):
        rc[svcName] = json.loads(config.getValue('services', svcName))

    return rc

def remove(name):
    config.remove('services', name)
