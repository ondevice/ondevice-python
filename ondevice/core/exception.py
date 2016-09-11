""" Some exception classes for the ondevice client """

class _Exception(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        self.msg = args[0]
        for k,v in kwargs.items():
            setattr(self, k, v)

class ConfigurationError(_Exception):
    """ Indicates a missing/faulty configuration value """
    pass

class ImplementationError(_Exception):
    """ Indicates implementation issues with a command or module """
    pass

class TransportError(_Exception):
    """ Indicates a communication error with the server """
    pass

class UsageError(_Exception):
    """ Indicates issues with the commandline usage (unknown command, unsupported argument, etc.) """
    pass
