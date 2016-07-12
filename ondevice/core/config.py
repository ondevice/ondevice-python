try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

import os

_config = None

def addSection(name):
    return _getConfig().add_section(name)

def getClientAuth(): return getValue('client', 'auth')
def getDeviceAuth(): return getValue('device', 'auth')
def getDeviceId(): return getValue('device', 'id')

def hasSection(name):
    return _getConfig().has_section(name)

def hasValue(section, name):
    return _getConfig().has_option(section, name)

def listKeys(section):
    return _getConfig().options(section)

def setClientAuth(auth): setValue('client', 'auth', auth)
def setDeviceAuth(auth): setValue('device', 'auth', auth)
def setDeviceId(devId): setValue('device', 'id', devId)
def setDeviceName(slug): setValue('device', 'name', slug)



def _getConfig():
    global _config
    if _config == None:
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
    cfg = _getConfig()
    if cfg.has_option(section, key):
        return cfg.get(section, key)
    else:
        return default

def remove(section, key):
    cfg = _getConfig()
    if not cfg.remove_option(section, key):
        raise KeyError("No such value: {0}/{1}".format(section, key))

    # TODO store a temporary file first (to avoid corrupting the config file in case of a full disk)
    cfgPath = _getConfigPath('ondevice.conf')
    with open(cfgPath, 'w') as f:
        cfg.write(f)

def setValue(section, key, value):
    cfg = _getConfig()
    cfg.set(section, key, value)

    # TODO store a temporary file first (to avoid corrupting the config file in case of a full disk)
    cfgPath = _getConfigPath('ondevice.conf')
    with open(cfgPath, 'w') as f:
        cfg.write(f)
