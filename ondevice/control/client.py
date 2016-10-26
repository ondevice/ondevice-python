
from ondevice.core import config, exception

from six.moves import urllib
import requests_unixsocket
import requests

ONDEVICE_HOST='http+unix://'+urllib.parse.quote(config._getConfigPath("ondevice.sock"), safe='')

_session = None

class Data:
    """ Slim wrapper around dict to make its items accessible via getattr() """
    def __init__(self, data):
        assert type(data) == dict
        self._data = data

    def __getattr__(self, key):
        rc = self._data[key]
        if type(rc) == dict:
            rc = Data(rc)
        return rc

    def __contains__(self, key):
        return key in self._data and self._data[key] != None

    def __repr__(self):
        return "Data({0})".format(repr(self._data))


def _getSession():
    """ Open and return a session on first use """
    global _session
    if _session == None:
        _session = requests_unixsocket.Session()
    return _session

def _makeUrl(endpoint, **params):
    global ONDEVICE_HOST
    parts = list(urllib.parse.urlsplit(ONDEVICE_HOST))
    parts[2] = endpoint

    if len(params) > 0:
        parts[3] = urllib.parse.urlencode(params)

    return urllib.parse.urlunsplit(parts)

def _getJson(endpoint, **params):
    try:
        url = _makeUrl(endpoint, **params)
        r = _getSession().get(url)
        if r.status_code >= 300:
            raise exception.TransportError("ondevice daemon responded with code {0}".format(r.status_code))
        return Data(r.json())
    except requests.exceptions.ConnectionError as e:
        raise exception.TransportError("failed to query ondevice daemon: {0}".format(e.args))


def getState(full=False):
    if full==False:
        return _getJson('/state')
    else:
        return _getJson('/state', full=full)
