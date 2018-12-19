import re
from pdfminer.layout import LTChar
from pdfxml.pdf_util.char_process import char_list2str
from pdfxml.pdf_util.layout_util import merge_bbox_list
# TODO, cross reference here
from pdfxml.marcos import LINE_TYPE_UNKNOWN


def get_head_prefix_pattern():
    """
    # head index, followed by dot and space,
    # and then a captialized character
    :return:
    """
    roman_numer = "I|II|III|IV|V|VI|VII"
    # start_pattern = r"^[ ]*((\d\.)+|(%s)\.|[A-Z]\.)[ ]*[A-Za-z]"%(roman_numer)
    start_pattern = r"^[ ]*(\d{1,2}|(\d{1,2}\.)+\d{0,1}|(%s)\.|[A-Z]\.{0,1})[ ]+"%(roman_numer)
    #[A-Z]\. is for IEEE standard.
    return start_pattern


def is_abstract_head(line_str):
    the_pattern = get_head_prefix_pattern()+"[ ]*Abstract[ ]*$"
    if re.match(the_pattern, line_str, re.I):
        return True
    if re.match(r"^[ ]*abstract[ ]*$", line_str, re.I):
        return True
    return False


def is_reference_head(line_str):
    the_pattern = get_head_prefix_pattern() + "[ ]*References[ ]*$"
    if re.match(the_pattern, line_str, re.I):
        return True
    if re.match(r"^[ ]*references[ ]*$", line_str, re.I):
        return True
    return False


def is_heading_line_by_str(line_str):
    """
    :param line_str:
    :return:
    """

    #print "might introduce false cases here"
    start_pattern = get_head_prefix_pattern()
    if re.match(start_pattern, line_str, re.I):
        return True
    # regex match, ignore the case
    if re.match(r"^[\d\. ]*Acknowledgements[ ]*$", line_str, re.I):
        return True
    if re.match(r"^[\d\. ]*Appendix[ ]*$", line_str, re.I):
        return True
    if re.match(r"^keywords", line_str, re.I):
        return True

    if is_reference_head(line_str):
        return True
    if is_abstract_head(line_str):
        return True

    return False


class LayoutLine:
    """
    What is line here? PDF line? PPC based line?
    Layout level
    """
    def __init__(self, chars, pid=None):
        """

        :param chars:
        :type chars: list[LTChar]
        :param pid:
        :type pid: int
        """
        self._chars = chars
        self.page = pid
        self.labels = []  # TODO, what label is this?
        self.type = LINE_TYPE_UNKNOWN

    def __str__(self):
        return self.get_line()

    def get_lt_chars(self):
        return self._chars

    def label_chars(self, prev_line, next_line):
        pass

    def print_chars(self):
        for c in self._chars:
            print c

    def print_line(self):
        print self.get_line().encode('utf-8')

    def get_line(self):
        line_str = char_list2str(self._chars)
        return line_str

    def check_line_section_title(self):
        line = self._chars
        line_str = self.get_line().strip()
        if len(line_str) < 2:
            return False

        if self.get_major_font() == "LURLGB+NimbusRomNo9L-Medi":
            return True

        if is_heading_line_by_str(line_str):
            return True

        return False

    def get_major_font(self):
        line = self._chars
        font2count = {}
        for char in line:
            if isinstance(char, LTChar):
                if not font2count.has_key(char.fontname):
                    font2count[char.fontname] = 0
                font2count[char.fontname] += 1
        font_list = font2count.keys()
        font_list.sort(key=lambda fn:-1*font2count[fn])
        return font_list[0]

    def get_bbox(self):
        bbox_list = [c.bbox for c in self._chars if isinstance(c, LTChar)]
        return merge_bbox_list(bbox_list)


"""
def test_one_pdf():
    from pdfxml.path_util import get_pdf_path_by_name
    from pdfxml.pdf_util.pdf_extract import get_page_num
    from pdfxml.me_extraction.me_font_stat_stage4 import internal_get_llines
    from pdfxml.pdf_util.char_process import char_list2str
    from pdfxml.loggers import doc_layout_logger
    pdf_name = "10.1.1.61.2493"
    pdf_path = get_pdf_path_by_name(pdf_name)
    pn = get_page_num(pdf_path)
    for pid in range(pn):
        lines = internal_get_llines(None, pdf_path, pid)
        for line in lines:
            line_str = char_list2str(line)
            is_heading = is_heading_line_by_str(line_str)
            doc_layout_logger.info("{} Heading:{}".format(
                line_str, is_heading
            ))
"""

if __name__ == "__main__":
    pass
    #test_one_pdf()
