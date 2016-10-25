"""
unix/tcp server socket used for communication with the ondevice daemon
"""

import ondevice
from ondevice.core import config
from ondevice.core import state as state_

import cherrypy
import json
import logging
import os
from six.moves import urllib

state = {}

class ControlSocket:
    def _toJson(self, data):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(data).encode('utf8')

    @cherrypy.expose
    def index(self):
        return ""

    @cherrypy.expose
    def state(self, full=False):
        s = state_.getCopy()
        rc = {
            'version': ondevice.getVersion()
        }

        # TODO add daemon status + device id

        if full:
            connections = []
            threads = []
            for key in ['connections', 'threads']:
                rc[key] = s[key] if key in s else None

        return self._toJson(rc)

_cherry = None



def setState(path, key, value):
    parent = _getPath(key, True)
    parent[key] = value

def start(ondeviceHost=None):
    global _cherry

    if _cherry != None:
        logging.info("Cherrypy has already been started")
        return

    if ondeviceHost == None and 'ONDEVICE_HOST' in os.environ:
        ondeviceHost = os.environ['ONDEVICE_HOST']
    if ondeviceHost == None:
        ondeviceHost = 'unix://'+config._getConfigPath('ondevice.sock')

    url = urllib.parse.urlparse(ondeviceHost)

    if url.scheme == 'unix':
        bindAddr = url.path
    elif url.scheme == 'http':
        bindAddr = (url.host, url.port)

    cherrypy.server.bind_addr = bindAddr
    cherrypy.tree.mount(ControlSocket(), '/')
    cherrypy.server.start()

    _cherry = cherrypy.server

def stop():
    cherrypy.server.stop()
