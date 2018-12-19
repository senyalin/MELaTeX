from pdfminer.layout import LTChar
from pdfxml.pdf_util.models.block import Block


class IMEBlock(Block):
    def __init__(self, chars):
        """

        :param chars: list of chars
        :type chars: LTChars
        """
        self._chars = chars
        # TODO, connect with layout analysis module
        self.parent = None

    def get_latex(self):
        from pdfxml.string_formatter import xw_join_string, xw_format_string
        latex_str = xw_join_string('', [
            c.get_text() for c in self._chars if isinstance(c, LTChar)])
        #latex_str = latex_str.encode("utf-8")
        return xw_format_string("${}$", [latex_str])
        #return "${}$".format(latex_str)

    def export_plain_txt(self):
        return self.get_latex()

    def set_parent(self, p):
        self.parent = p

    def get_font(self):
        if self.parent is None:
            raise Exception("Should construct the hierarcy")
        return self.parent.get_font()