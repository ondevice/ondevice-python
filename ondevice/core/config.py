from configparser import ConfigParser
import os

_config = None

def getClientAuth(): return _getValue('client', 'auth')
def getDeviceAuth(): return _getValue('device', 'auth')
def getDeviceId(): return _getValue('device', 'id')

def setClientAuth(auth): _setValue('client', 'auth', auth)
def setDeviceAuth(auth): _setValue('device', 'auth', auth)
def setDeviceId(devId): _setValue('device', 'id', devId)


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

    return _config

def _getConfigPath(filename):
    # TODO add proper support for other OSes
    # TODO handle missing ~/.config dir
    homeDir = os.path.expanduser('~')
    configDir = os.path.join(homeDir, '.config/ondevice')
    if not os.path.isdir(configDir):
        os.mkdir(configDir)

    return os.path.join(configDir, filename)

def _getValue(section, key, default=None):
    cfg = _getConfig()
    if cfg.has_option(section, key):
        return cfg.get(section, key)
    else:
        return default

def _setValue(section, key, value):
    cfg = _getConfig()
    cfg.set(section, key, value)

    # TODO store a temporary file first (to avoid corrupting the config file in case of a full disk)
    cfgPath = _getConfigPath('ondevice.conf')
    with open(cfgPath, 'w') as f:
        cfg.write(f)
