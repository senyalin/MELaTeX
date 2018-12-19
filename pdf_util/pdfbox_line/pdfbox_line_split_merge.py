"""
Split and merging of the PDFBox Lines
"""
import numpy as np

from pdfxml.loggers import pdf_util_error_log, pdf_util_debug_log
from pdfxml.pdf_util.bbox import BBox
from pdfxml.pdf_util.unionfind import UnionFind
from pdfxml.pdf_util.word_chunking_model.max_word_num import max_word_split
from pdfxml.pdf_util.word_seg_process import get_char_list_list, char_list_list2char_list
from pdfxml.pdf_util.layout_util import get_char_list_bbox
from pdfxml.pdf_util.char_process import char_list2str


def check_pdfbox_word_segmentation_fail(char_list_list, word_info_list):
    """

    :param char_list_list:
    :param word_info_list:
    :return:
    """
    CHECK_PDFBOX_FAIL_THRES = 0.5
    line_bbox_list = []
    line_width_list = []
    for char_list_line in char_list_list:
        line_bbox = get_char_list_bbox(char_list_line)
        line_bbox_list.append(line_bbox)
        line_width_list.append(line_bbox.width())

    line_width_median = np.percentile(line_width_list, 95)

    failed_count = 0
    for word_info in word_info_list:
        if BBox(word_info['bbox']).width() > CHECK_PDFBOX_FAIL_THRES * line_width_median:
            failed_count += 1
    return failed_count > CHECK_PDFBOX_FAIL_THRES * len(word_info_list)


WORD_LENGTH_95_QUARTILE = 15
def get_longest_length(char_list_list):
    """

    :param char_list_list:
    :return:
    """
    assert len(char_list_list) > 0
    max_len = -1
    for char_list in char_list_list:
        if len(char_list) > max_len:
            max_len = len(char_list)
    return max_len


def merging_merge_one_line(char_list_line, word_info_list):
    """
    merge the word in a line based on the overlapping with the word extracted from pdfbox

    :param char_list_line:
    :param word_info_list:
    :return:
    """
    # out put some debuging information here.
    pdf_util_debug_log.debug(char_list2str(char_list_line))
    line_bbox = get_char_list_bbox(char_list_line)
    pdfbox_word_bbox_list = []
    for word_info in word_info_list:
        if line_bbox.overlap(word_info['bbox']):
            pdfbox_word_bbox_list.append(word_info['bbox'])

    # get the bbox and overlapped word bbox
    # build a confusion matrix of the word.
    char_word_list = get_char_list_list(char_list_line)
    char_word_bbox_list = []
    for wid, char_word in enumerate(char_word_list):
        char_word_bbox_list.append(get_char_list_bbox(char_word))
        pdf_util_debug_log.debug("{} {}".format(wid, char_list2str(char_word)))

    # build the overlapping matrix here.
    # two should be merged if they overlap with the same word from pdfbox
    # union find algorithm here to find connected components.
    uf = UnionFind()
    for cid, char_word_bbox in enumerate(char_word_bbox_list):
        uf.add_node(cid)

    for pid, pdfbox_word_bbox in enumerate(pdfbox_word_bbox_list):
        cid_list = []
        for cid, char_word_bbox in enumerate(char_word_bbox_list):
            if char_word_bbox.overlap(pdfbox_word_bbox):
                cid_list.append(cid)
        for cid in cid_list:
            uf.merge(cid_list[0], cid)

    merged_cid_list_list = uf.get_groups()
    new_char_word_list = []
    new_char_word_bbox_list = []
    for merged_cid_list in merged_cid_list_list:
        tmp_char_word = []
        for cid in merged_cid_list:
            tmp_char_word.extend(char_word_list[cid])
        new_char_word_list.append(tmp_char_word)
        new_char_word_bbox_list.append(get_char_list_bbox(tmp_char_word))

    # for the lesft cid_list

    # sort based on the left boundary
    tmp_idx_list = range(len(new_char_word_list))
    tmp_idx_list.sort(key=lambda idx: new_char_word_bbox_list[idx].left())
    sorted_new_char_word_list = []
    for tmp_idx in tmp_idx_list:
        sorted_new_char_word_list.append(new_char_word_list[tmp_idx])

    # TODO, split the lines with too long word, very likely to be wrong
    max_len = get_longest_length(sorted_new_char_word_list)
    if max_len > WORD_LENGTH_95_QUARTILE:
        new_char_list_line = max_word_split(char_list_line)
    else:
        new_char_list_line = char_list_list2char_list(sorted_new_char_word_list)

    return new_char_list_line


def merging_oversplit_pdfbox(char_list_list, word_info_list):
    """
    my own algorithm of splitting is based on a threshold, which might be too small
    so that many words are split into multiple parts.

    This function will try to merge them

    :param char_list_list:
        list of lines
    :param word_info_list:
        word information is from the output of PDFBox,
        If the pdfbox is not good, it will downgrade to the pdfminer
        If still not good, will degrade to the max util DP
    :return:
    """
    new_char_list_list = []

    pdfbox_segment_fail = check_pdfbox_word_segmentation_fail(char_list_list, word_info_list)
    if pdfbox_segment_fail:  # failed checking
        pdf_util_error_log.error("Failed pdfbox checking, todo, pass the file name here")
        new_char_list_list = []
        for char_list in char_list_list:
            new_char_list_list.append(max_word_split(char_list))
        #return char_list_list
        return new_char_list_list

    for char_list_line in char_list_list:
        new_char_list_line = merging_merge_one_line(char_list_line, word_info_list)
        new_char_list_list.append(new_char_list_line)

    return new_char_list_list