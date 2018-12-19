BLOCK_TYPE_IME, \
    BLOCK_TYPE_PARAGRAPH, \
    BLOCK_TYPE_FIGURE, \
    BLOCK_TYPE_TABLE = range(4)


class Block(object):
    """
    This is an abstract class

    block could be a paragraph, IME, Figure, Table, etc.

    TODO, the figure/table processing should be based on the
    AAAI workshop paper
    """
    def __init__(self):
        """

        """
        self.type = None  # BLOCK_TYPE_IME, BLOCK_TYPE_PARAGRAPH
        self.llines = []  # layout lines for paragraph
