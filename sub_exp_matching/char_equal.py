"""
Check whether two chars are equal
"""

from pdfxml.me_extraction.me_consts import CHAR_EQUAL_V, \
    CHAR_EQUAL_GN_FN, CHAR_EQUAL_GN


def char_same(char1, char2):
    """
    assume the get_text return the glyph name

    :param char1:
    :param char2:
    :return:
    """
    if CHAR_EQUAL_V == CHAR_EQUAL_GN:
        raise Exception("TODO")
    elif CHAR_EQUAL_V == CHAR_EQUAL_GN_FN:
        return char1.get_text() == char2.get_text() and \
            char1.fontname == char2.fontname
    else:
        raise Exception('unknown char sameness checking')
