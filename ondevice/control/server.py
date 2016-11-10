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

def _getSocketUrl():
    rc = None
    if 'ONDEVICE_HOST' in os.environ:
        rc = os.environ['ONDEVICE_HOST']
    if rc == None:
        rc = 'unix://'+config._getConfigPath('ondevice.sock')
    return rc


def start():
    global _cherry

    if _cherry != None:
        logging.info("Cherrypy has already been started")
        return

    socketUrl = _getSocketUrl()
    url = urllib.parse.urlparse(socketUrl)

    if url.scheme == 'unix':
        bindAddr = url.path
    elif url.scheme == 'http':
        bindAddr = (url.host, url.port)

    cherrypy.server.bind_addr = bindAddr
    cherrypy.tree.mount(ControlSocket(), '/')
    cherrypy.server.start()

    if url.scheme == 'unix':
        os.chmod(url.path, 0o660)

    _cherry = cherrypy.server

def stop():
    cherrypy.server.stop()

    # remove unix socket file
    sock = urllib.parse.urlsplit(_getSocketUrl())
    if sock.scheme == 'unix':
        if os.path.exists(sock.path):
            os.unlink(sock.path)
    
    
