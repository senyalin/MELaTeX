"""
extract the information based on the pdfbox

pdf_extract_lines:
    the main interface
    will detect whether it's single or double column based on the ratio of lines under the threshold
    given the raw line extracted, the line will go through the line merging process.

"""
import os

from pdfxml.path_util import get_tmp_path
from pdfxml.pdf_util.pdfbox_layout import is_double_column
from pdfxml.pdf_util.pdfbox_line_merging import merging_lines, word_info_filter
from pdfxml.pdf_util.pdfbox_line_merging import pdf_extract_lines_raw
from pdfxml.pdf_util.pdfbox_wrapper import get_pdf_page_size
from pdfxml.pdf_util.pdfbox_wrapper import pdf_extract_words, pdf_extract_fontname2space
from pdfxml.file_util import load_serialization, dump_serialization


###########
# get the chars
###########
def pdf_extract_lines(pdf_path, pid=0, force_single=False):
    """
    each line is a list of LTChar

    :param pdf_path:
    :param pid:
    :return:
    """
    tmp_pdf_path = get_tmp_path(pdf_path)
    cache_path = "{}.pdfbox_merge_line.{}.pkl".format(tmp_pdf_path, pid)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    char_list_list = pdf_extract_lines_raw(pdf_path, pid)

    # TODO, do another round of line merging
    # still use our column line detection model to find the region.
    fontname2space = pdf_extract_fontname2space(pdf_path, pid)
    word_info_list = pdf_extract_words(pdf_path, pid)

    res_char_list_list = []
    if not force_single and is_double_column(pdf_path, pid):
        # split the current list into three parts
        # detect the center split, create two column
        # outside of the double column,
        # within the double column
        page_size = get_pdf_page_size(pdf_path, pid)
        page_width = page_size['width']

        out_char_list_list = []
        left_char_list_list = []
        right_char_list_list = []
        from pdfxml.pdf_util.layout_util import get_char_list_bbox
        for char_list in char_list_list:
            bbox = get_char_list_bbox(char_list)
            if bbox.left() < bbox.right() < page_width / 2:
                left_char_list_list.append(char_list)
            elif bbox.right() > bbox.left() > page_width / 2:
                right_char_list_list.append(char_list)
            else:
                out_char_list_list.append(char_list)

        # before mering do the word_info_filter
        word_info_list = word_info_filter(char_list_list, word_info_list)

        new_out_char_list_list = merging_lines(out_char_list_list, fontname2space, word_info_list, pdf_path, pid)
        new_left_char_list_list = merging_lines(left_char_list_list, fontname2space, word_info_list, pdf_path, pid)
        new_right_char_list_list = merging_lines(right_char_list_list, fontname2space, word_info_list, pdf_path, pid)

        # not in the vertical range of the double dolumn
        # center on the left part,
        # center on the right part,
        char_list_list = []
        char_list_list.extend(new_out_char_list_list)
        char_list_list.extend(new_left_char_list_list)
        char_list_list.extend(new_right_char_list_list)

        res_char_list_list =  char_list_list
    else:
        # before mering do the word_info_filter
        word_info_list = word_info_filter(char_list_list, word_info_list)

        # single column, then just go on merging the lines
        new_char_list_list = merging_lines(char_list_list, fontname2space, word_info_list, pdf_path, pid)
        res_char_list_list = new_char_list_list
    dump_serialization(res_char_list_list, cache_path)
    return res_char_list_list

