try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

import os

class Overrides:
    def __init__(self):
        self.data = {}

    def __contains__(self, key):
        return key in self.data

    def clear(self):
        self.data = {}

    def get(self, section, key, default=None):
        if not (section,key) in self.data:
            return default
        return self.data[(section,key)]

    def items(self):
        for key, value in self.data.items():
            yield key[0], key[1], value

    def put(self, section, key, value):
        self.data[(section,key)] = value

    def remove(self, section, key):
        if (section, key) in self.data:
            del(self.data[(section,key)])

_config = None
overrides = Overrides()

def addSection(name):
    return _getConfig(True).add_section(name)

def getClientAuth(tgtUser=None):
    clientUser = getValue('client', 'user')
    if tgtUser != None:
        if tgtUser != clientUser:
            userKey = 'auth_{0}'.format(tgtUser)
            if hasValue('client', userKey):
                return tgtUser, getValue('client', userKey)
    clientKey = getValue('client', 'auth')
    if clientUser != None and clientKey != None:
        return clientUser, getValue('client', 'auth')
    else: return None

def getDeviceAuth(): return getValue('device', 'auth')
def getDeviceId(): return getValue('device', 'id')
def getDeviceUser():
    # code to fix backwards compatibility
    # TODO remove this snippet as soon as all devices are updated
    if not hasValue('device', 'user') and hasValue('device', 'name'):
        rc = getValue('device', 'name').split('/')[0]
        setDeviceUser(rc)
        return rc
    else:
        return getValue('device', 'user')

def hasSection(name):
    return _getConfig().has_section(name)

def hasValue(section, name):
    return _getConfig().has_option(section, name)

def listKeys(section):
    return _getConfig().options(section)

def setClientAuth(auth): setValue('client', 'auth', auth)
def setClientUser(name): setValue('client', 'user', name)
def setDeviceAuth(auth): setValue('device', 'auth', auth)
def setDeviceId(devId): setValue('device', 'id', devId)
def setDeviceName(slug): setValue('device', 'name', slug)
def setDeviceUser(name): setValue('device', 'user', name)



def _getConfig(reread=False):
    global _config
    if reread == True or _config == None:
        configFile = _getConfigPath('ondevice.conf')
        _config = ConfigParser()
        _config.read(configFile)

        # init sections
        for s in ['client', 'device']:
            if not _config.has_section(s):
                _config.add_section(s)
        if not _config.has_section('services'):
            _config.add_section('services')
            _config.set('services', 'ssh', '{"protocol": "ssh"}')

    return _config

def _getConfigPath(filename):
    # TODO add proper support for other OSes
    # TODO handle missing ~/.config dir
    homeDir = os.path.expanduser('~')
    configDir = os.path.join(homeDir, '.config/ondevice')
    if not os.path.isdir(configDir):
        os.mkdir(configDir)

    return os.path.join(configDir, filename)

def getValue(section, key, default=None):
    if (section,key) in overrides:
        return overrides.get(section, key, default)

    cfg = _getConfig()
    if cfg.has_option(section, key):
        return cfg.get(section, key)
    else:
        return default

def remove(section, key):
    cfg = _getConfig(True)
    if not cfg.remove_option(section, key):
        raise KeyError("No such value: {0}/{1}".format(section, key))

    _saveConfig()

def setValue(section, key, value):
    cfg = _getConfig(True)
    overrides.remove(section, key)
    cfg.set(section, key, value)
    _saveConfig()

def _saveConfig():
    cfg = _getConfig()
    cfgPath = _getConfigPath('ondevice.conf')
    tmpPath = os.path.join(os.path.dirname(cfgPath), '.{0}.tmp'.format(os.path.basename(cfgPath)))
    with open(tmpPath, 'w') as f:
        cfg.write(f)
    os.rename(tmpPath, cfgPath)
