"""
Different situation,
organized as subclass of Exception,
which need to be taken care of later
"""


class TooLongException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Too long with {} elements".format(self.value)


class SqrtProcessingException(Exception):
    def __init__(self, detail):
        self.detail = detail

    def __str__(self):
        return "Sqrt related error: {}".format(self.detail)


class ComponentEmptyException(Exception):
    def __init__(self):
        pass


class NoneMEGroupException(Exception):
    """
    should not have value None as MEGroup
    """
    def __init__(self):
        pass


class LeftRelationException(Exception):
    """
    currently don't support left relation yet
    """
    def __init__(self):
        pass


class VerticalBarException(Exception):
    def __init__(self):
        pass