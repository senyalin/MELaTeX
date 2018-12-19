"""
Page is a layout concept
"""
from pdfxml.marcos import LINE_IME, LINE_TYPE_SECTION
from pdfxml.pdf_util.pdf_extract import get_page_num
from pdfxml.pdf_util.layout_util import bbox_half_overlap_list
from pdfxml.pdf_util.models.layout_line import LayoutLine
# TODO, move to the MEExtraction module
from pdfxml.me_util import load_ime_bbox_list
from pdfxml.me_extraction.me_font_stat_stage4 import internal_get_llines


class LayoutPage(object):
    """

    """
    def __init__(self, pdf_path, pid):
        """

        :param pdf_path:
        :type pdf_path: str
        :param pid:
        :type pid: int
        """
        pn = get_page_num(pdf_path)
        if pid >= pn:
            raise Exception("page size exceed")

        self.pdf_path = pdf_path
        self.pid = pid
        self.llines = []  # LayoutLine list

        char_list_list = internal_get_llines(None, pdf_path, pid)
        for char_list in char_list_list:
            line = LayoutLine(char_list, pid)
            self.llines.append(line)

        ime_bbox_list = load_ime_bbox_list(pdf_path, pid)
        for ll in self.llines:
            ":type ll:LayoutLine"
            if bbox_half_overlap_list(ll.get_bbox(), ime_bbox_list):
                ll.type = LINE_IME

            # TODO, check heading
            # TODO, customized for each conference
            if ll.check_line_section_title():
                ll.type = LINE_TYPE_SECTION

    def __str__(self):
        return "Page {} of {}".format(self.pid, self.pdf_path)

    def get_layout_lines(self):
        return self.llines
