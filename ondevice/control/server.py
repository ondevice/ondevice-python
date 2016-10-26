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
import threading
from six.moves import urllib

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

        stateKeys = ['device']
        if full:
            stateKeys.extend(['tunnels'])

            if 'threads' in full:
                # print system threads instead of BackgroundThread instances
                rc['threads'] = []
                for t in threading.enumerate():
                    rc['threads'].append({'name': t.name, 'daemon': t.daemon, 'id': t.ident})
            else:
                stateKeys.append('threads')

        for key in stateKeys:
            if key in s:
                rc[key] = s[key]

        return self._toJson(rc)

_cherry = None


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
