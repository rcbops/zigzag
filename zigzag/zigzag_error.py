class ZigZagError(Exception):
    """An base Error used by ZigZag"""

    def __init__(self, message):
        super(ZigZagError, self).__init__(message)


class ZigZagConfigError(ZigZagError):
    """An Error raised in loading and accessing ZigZag's config file"""

    def __init__(self, message):
        super(ZigZagConfigError, self).__init__(message)


class ZigZagRequiredPropertyError(ZigZagError):
    """An Error raised when a required property can not be found"""

    def __init__(self, message):
        super(ZigZagConfigError, self).__init__(message)
