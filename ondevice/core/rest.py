import ondevice
from ondevice.core import config, sock

import base64
import json
import logging

try:
    from http.client import HTTPConnection, HTTPSConnection
except ImportError:
    from httplib import HTTPConnection, HTTPSConnection

def apiDELETE(endpoint, params={}, data=None):
    return apiRequest('DELETE', endpoint, params=params, data=data)

def apiGET(endpoint, params={}):
    return apiRequest('GET', endpoint, params=params)

def apiPOST(endpoint, params={}, data=None):
    return apiRequest('POST', endpoint, params=params, data=data)

def apiRequest(method, endpoint, params={}, data=None):
    # TODO implement URL params support
    auth = config.getClientAuth()
    headers = {}

    if auth != None:
        basicAuth = base64.b64encode("{0}:{1}".format(*auth).encode('ascii')).decode('ascii')
        headers['Authorization'] = 'Basic {0}'.format(basicAuth)

    # parse data:
    if data != None:
        data = json.dumps(data)
        headers.update({
            'Content-type': 'application/json; charset=utf8',
            'User-agent': 'ondevice v{0}'.format(ondevice.getVersion())
        }) # TODO check if we need to also set the content-length

    if sock.BASE_URL.scheme == 'ws':
        c = HTTPConnection(sock.BASE_URL.hostname, sock.BASE_URL.port)
    elif sock.BASE_URL.scheme == 'wss':
        c = HTTPSConnection(sock.BASE_URL.hostname, sock.BASE_URL.port)
    # TODO do proper URL handling (urllib)
    c.request(method, '/v1.1{0}'.format(endpoint), body=data, headers=headers)
    resp = c.getresponse()
    rc = resp.read()

    if resp.status < 200 or resp.status >= 300:
        # TODO implement HTTP redirect support
        logging.warning("Error message: %s", rc)
        raise Exception("API server responded with code {0}!".format(resp.status))
    elif 'content-type' not in resp.headers:
        raise Exception("Response lacks Content-type header!")

    cType=resp.headers['content-type'].lower().split(';')
    if cType[0] != 'application/json':
        raise Exception("Expected an 'application/json' response (was: '{0}')".format(cType[0]))
    if type(rc) == bytes:
        rc = rc.decode('utf8') # TODO check the actual 'charset' part from cType
    return json.loads(rc)
