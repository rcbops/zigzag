class ZigZagError(Exception):
    """An base Error used by ZigZag"""

    def __init__(self, message):
        super(ZigZagError, self).__init__(message)
