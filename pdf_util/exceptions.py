class UnknownGlyphName(Exception):
    """

    """
    def __init__(self, gn):
        self.gn = gn
        Exception.__init__(self, gn)

    def __str__(self):
        return "unknown glyph name {}".format(self.gn)

    def __repr__(self):
        return self.__str__()


class UnknownUnicodeException(Exception):
    def __init__(self, uval):
        self.uval = uval

    def __str__(self):
        return "unknown unicode value {} {}".format(
            self.uval.encode('utf-8'),
            self.uval.encode('raw_unicode_escape'),
        )

    def __repr__(self):
        return self.__str__()