""" Some exception classes for the ondevice client """


class ConfigurationError(Exception):
    """ Indicates a missing/faulty configuration value """
    pass

class ImplementationError(Exception):
    """ Indicates implementation issues with a command or module """
    pass

class TransportError(Exception):
    """ Indicates a communication error with the server """
    pass

class UsageError(Exception):
    """ Indicates issues with the commandline usage (unsupported argument, etc.) """
    pass
