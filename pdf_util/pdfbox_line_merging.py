"""

merging_lines:
    This is the main API

pdf_extract_line_raw:
    using the stream order of the char, to merge the vertically overlapping ones

"""
import pdfxml.pdf_util.macros as pdf_util_settings
from pdfminer.layout import LTChar, LTAnno
from pdfxml.pdf_util.bbox import BBox
from pdfxml.pdf_util.char_process import is_space_char, char_list2bbox
from pdfxml.pdf_util.layout_util import get_char_list_bbox, merge_bbox_list
from pdfxml.pdf_util.word_seg_process import re_group_char_list_seg, char_list_list2char_list
from pdfxml.pdf_util.pdfbox_wrapper import pdf_extract_fontname2space, pdf_extract_chars
from pdfxml.pdf_util.pdfbox_line.pdfbox_line_empty import remove_empty_lines
from pdfxml.pdf_util.pdfbox_line.pdfbox_line_accent import merge_accent
from pdfxml.pdf_util.pdfbox_line.pdfbox_line_ime import merge_line_ime
from pdfxml.pdf_util.pdfbox_line.pdfbox_line_split_merge import merging_oversplit_pdfbox


def split_by_space_char_list_list(char_list_list):
    """
    unify and change the space into LTAnno

    TODO, not quite sure about the logic here,
    seeem to be override by sth...

    :return:
    """
    new_char_list_list = []
    for char_list in char_list_list:
        new_char_list = []
        for char in char_list:
            if is_space_char(char):
                # TODO, I am not quite sure about the logic here
                # it seems that I change it to keep the space char
                if len(new_char_list) > 0 and not is_space_char(new_char_list[-1]):
                    new_char_list.append(LTAnno(" "))
            else:
                new_char_list.append(char)
        new_char_list_list.append(new_char_list)
    return new_char_list_list


def merge_line_basic(char_list_list, fontname2space):
    """
    with bugs of creating duplicate characters

    after the accent is merge with the corresponding line

    first, sort the lines based on the top position
    then, merge the lines that overlap with 0.5 of the height

    :param char_list_list:
    :return:
    """
    if len(char_list_list) == 0:
        return char_list_list

    line_bbox_list = []
    for char_list in char_list_list:
        # remove the accent is to avoid over merging.
        line_bbox = get_char_list_bbox(char_list, remove_accent=True)

        # adjust to reduce the height by 1/3
        line_bbox = BBox([
            line_bbox.left(),
            line_bbox.bottom()+line_bbox.height()/6,
            line_bbox.right(),
            line_bbox.top()-line_bbox.height()/6
        ])

        line_bbox_list.append(line_bbox)

    cur_line_idx_list = range(len(char_list_list))
    cur_line_idx_list.sort(key=lambda lid: -line_bbox_list[lid].top())

    tmp_char_list = []
    tmp_bbox = line_bbox_list[cur_line_idx_list[0]]

    # create debug information here about the merging
    line_str = []
    try:
        for sort_lid in cur_line_idx_list:
            tmp_str = ""
            for char in char_list_list[sort_lid]:
                tmp_str += char.get_text()
            line_str.append(tmp_str)
    except Exception as e:
        print 'create debug information error'
        pass

    # the accent merging here.
    return_char_list_list = []
    for i, sort_lid in enumerate(cur_line_idx_list):
        # if vertical overlapping larger 0.5 of each, then merging,
        # other wise, dont merge

        #if tmp_bbox.v_overlap(line_bbox_list[sort_lid], 0.5):
        # hat not be part of the calculation
        if tmp_bbox.v_overlap(line_bbox_list[sort_lid]):
            tmp_char_list.extend(char_list_list[sort_lid])
            tmp_bbox = merge_bbox_list(
                [tmp_bbox, line_bbox_list[sort_lid]])
        else:
            tmp_char_list = [c for c in tmp_char_list if isinstance(c, LTChar)]
            tmp_char_list.sort(key=lambda c: c.bbox[0])
            return_char_list_list.append(
                re_group_char_list_seg(tmp_char_list, fontname2space))

            # create a new line to merge
            tmp_char_list = []
            tmp_char_list.extend(char_list_list[sort_lid])
            tmp_bbox = line_bbox_list[sort_lid]

    if len(tmp_char_list) > 0:
        return_char_list_list.append(
            re_group_char_list_seg(tmp_char_list, fontname2space))
    return return_char_list_list


def word_info_filter(char_list_list, word_info_list):
    """
    pass in all lines

    :param char_list_list:
    :param word_info_list:
    :return:
    """
    # remove bbox that span multiple lines
    # 2D overlapping finding.
    from pdfxml.intervaltree_2d import IntervalTree2D
    line_interval_tree_2d = IntervalTree2D()
    for i, char_list_line in enumerate(char_list_list):
        line_bbox = get_char_list_bbox(char_list_line)
        line_interval_tree_2d.add_bbox(i, line_bbox)
    filtered_word_info_list = []
    for word_info in word_info_list:
        line_name_list = line_interval_tree_2d.get_overlap_by_bbox(word_info['bbox'])
        if len(line_name_list) > 1:
            msg = "one word overlap with multipe lines {}".format(word_info)
            print msg
            continue
        filtered_word_info_list.append(word_info)
    word_info_list = filtered_word_info_list
    return word_info_list


def merging_lines(char_list_list, fontname2space, word_info_list=None, pdf_path=None, pid=None):
    """
    merge accent, will try to merge each accent symbol with word first

    :param word_info_list:
    :param fontname2space:
    :param char_list_list:
    :return:
        still return list of char_list,
        but merge the vertical overlapping ones
    """
    if len(char_list_list) == 0:
        return char_list_list

    # the accent line only merge with the following line
    char_list_list = merge_accent(char_list_list, fontname2space)

    # based on the vertical overlapping
    char_list_list = merge_line_basic(char_list_list, fontname2space)

    # the binding variable range should be merged with the big operators
    char_list_list = merge_line_ime(char_list_list)

    # the last step of grouping based on the word boundary from the pdf_bbox
    if word_info_list is not None:
        char_list_list = merging_oversplit_pdfbox(char_list_list, word_info_list)

    if pdf_util_settings.MERGE_FRACTION_LINE:
        from pdfxml.pdf_util.pdfbox_line.pdfbox_line_fraction import merge_line_fraction
        from pdfxml.pdf_util.path_processing.get_fraction_paths import get_fraction_line
        if pdf_path is None or pid is None:
            raise Exception("need the pdf path and pid to get the fraction lines")
        fraction_path_list = get_fraction_line(pdf_path, pid)
        # only keep the fractionline that lies in the bounding box of the columns
        tmp_char_list = char_list_list2char_list(char_list_list)
        tmp_bbox = char_list2bbox(tmp_char_list)
        fraction_path_list = [path for path in fraction_path_list if tmp_bbox.contains(path.bbox)]
        char_list_list = merge_line_fraction(char_list_list, fraction_path_list)

    # the last step of splitting by the space, as the space is kept
    char_list_list = split_by_space_char_list_list(char_list_list)

    return char_list_list


def pdf_extract_lines_raw(pdf_path, pid=0):
    """
    each line is a list of LTChar

    based on the order of the original elements.

    :param pdf_path:
    :param pid:
    :return:
    """
    fontname2space = pdf_extract_fontname2space(pdf_path, pid)
    char_list = pdf_extract_chars(pdf_path, pid)
    char_list_list = list()
    if len(char_list) == 0:
        return char_list_list
    cur_bbox = BBox(char_list[0].bbox)
    tmp_char_list = list()
    for i, char in enumerate(char_list):
        tmp_bbox = BBox(char.bbox)
        if cur_bbox.v_overlap(tmp_bbox):
            tmp_char_list.append(char)
        else:
            tmp_char_list.sort(key=lambda char_arg:char_arg.bbox[0])
            char_list_list.append(
                re_group_char_list_seg(tmp_char_list, fontname2space))
            tmp_char_list = [char]
            cur_bbox = BBox(char.bbox)

    if len(tmp_char_list) > 0:
        char_list_list.append(
            re_group_char_list_seg(tmp_char_list, fontname2space))

    # clean the lines with only LTAnno
    char_list_list = remove_empty_lines(char_list_list)

    return char_list_list

