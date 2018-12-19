"""
Estimation of the space between the consecutive chars within a word
or the consecutive chars between words
"""
import string

import numpy as np
import nltk

# TODO if  user is apache, 
nltk.data.path.append("/home/grads/x/xingwang/nltk_data")
nltk.data.path.append("/home/shared/nltk_data")

from nltk.corpus import words

from pdfminer.layout import LTChar, LTAnno
from pdfxml.pdf_util.bbox import BBox
from pdfxml.pdf_util.char_process import get_latex_val_of_lt_char, char_list2str
from pdfxml.pdf_util.macros import MERGE_ISOLATED_DIGIT, SPLIT_UNPAIRED_PARENTHESIS
from pdfxml.pdf_util.pdf_extract import process_pdf_lines, get_page_num

from pdfxml.me_taxonomy.latex.latex_op import is_bin_op_latex_val
from pdfxml.me_taxonomy.latex.latex_rel import is_rel_latex_val

word_set = set(words.words())
SPACE_THRES_RATIO = 0.3


def create_char(char, val, fontname=None, bbox=None):
    """
    For testing purpose utility

    :param char:
    :type char: LTChar
    :param val: the unicode value for the char, might be null if don't have unicode value
    :return:
    """
    import copy
    res_char = copy.copy(char)
    res_char._text = val
    if fontname is not None:
        res_char.fontname = fontname
    if bbox is not None:
        res_char.set_bbox(bbox)
    return res_char


def group_line_into_words(line, check_nltk=False):
    """
    TODO, This looks challenging? or what is done here?

    :param line:
    :return: list of list of LTChar
    """
    word_list = []
    word_char_list = []
    for c in line:
        if isinstance(c, LTAnno):
            if len(word_char_list) > 0:
                tmp_str = char_list2str(word_char_list)
                if check_nltk:
                    if tmp_str in word_set:
                        word_list.append(word_char_list)
                    else:
                        # ignore the current one
                        word_list.append([])
                else:
                    word_list.append(word_char_list)
            word_char_list = []
        elif isinstance(c, LTChar):
            word_char_list.append(c)
        else:
            raise Exception('unknown char type')
    if len(word_char_list) > 0:
        word_list.append(word_char_list)
    # each word is a list of char
    return word_list


def get_char_dist_est_line(line):
    """
    get the mean between consectuve chars wthin and between words

    :param line: list of LTChar or LTAnno
    :return:
    """
    within_dist_list = []
    between_dist_list = []
    word_list = group_line_into_words(line)
    word_str_list = []
    for word in word_list:
        word_str_list.append(char_list2str(word))
    for i in range(len(word_list)-1):
        if len(word_list[i+1]) == 0 or len(word_list[i]) == 0:
            continue
        between_dist = word_list[i+1][0].bbox[0] - word_list[i][-1].bbox[2]
        if between_dist < -10:
            continue
        between_dist_list.append(between_dist)
    for word in word_list:
        for i in range(len(word)-1):
            within_dist = word[i+1].bbox[0] - word[i].bbox[2]
            if within_dist < -10:
                continue
            within_dist_list.append(within_dist)
    return within_dist_list, between_dist_list


def get_char_dist_est(pdf_path):
    """
    get the parameter estimation for brand new word segmenter

    :param pdf_path:
    :return:
    """

    pn = get_page_num(pdf_path)
    within_dist_list = []
    between_dist_list = []
    for pid in range(pn):
        #lines = ppc_line_reunion(pdf_path, pid)
        lines = process_pdf_lines(pdf_path, pid)
        # for each line, group into list of words
        for line in lines:
            wi_list, bn_list = get_char_dist_est_line(line)
            within_dist_list.extend(wi_list)
            between_dist_list.extend(bn_list)
    return within_dist_list, between_dist_list


def char_list2char_list_list(char_list_in, check_order=False):
    """
    A simple wrapper to meet my conceptual model
    :param char_list_in:
    :return:
    """
    return get_char_list_list(char_list_in, check_order)


def get_char_list_list(char_list_in, check_order=False):
    """
    Based on existing word segmenter, adjust for analysis purpose

    group the chars into words

    Example for not order by left boundary: the accent is before the char, but left boundary not.

    :param char_list:
    :return:
    """
    if len(char_list_in) == 0:
        return []

    # need to assert the char_list_in is sorted by the left boundary if possible
    if check_order:
        cur_left = None
        for char in char_list_in:
            if isinstance(char, LTChar):
                if cur_left is not None and char.bbox[0] < cur_left:
                    raise Exception("The char list is not ordered by left position")
                cur_left = char.bbox[0]

    char_list_list = []
    char_list = []
    for c in char_list_in:
        if isinstance(c, LTChar):
            char_list.append(c)
        else:
            if len(char_list) > 0:
                char_list_list.append(char_list)
            char_list = []
    if len(char_list) > 0:
        char_list_list.append(char_list)
    return char_list_list


def char_list_list2char_list(char_list_list, nscs_bbox_list=None):
    """
    sort based on left2right,

    TODO, and also merge those with horizontal overlapping, interval merging
    not merging for now, as still might merge on the post processing


    :param tmp_nscs_bbox_list:
    :param char_list_list:
    :return:
    """
    # do a preprocessing here to remove empty char_list
    char_list_list = [
        char_list for char_list in char_list_list if len(char_list) > 0
    ]

    if nscs_bbox_list is not None:
        assert len(char_list_list) == len(nscs_bbox_list)
        idx_list = range(len(char_list_list))
        idx_list.sort(key=lambda i: nscs_bbox_list[i].left())
    else:
        idx_list = range(len(char_list_list))
        # try to do a bit sort here

        char_list_list.sort(key=lambda char_list:char_list[0].bbox[0])
        # TODO, try to assert the input is sorted

        for i in range(1, len(char_list_list)):
            if len(char_list_list[i]) == 0:
                pass
            assert len(char_list_list[i]) > 0
            if char_list_list[i][0].bbox[0] < char_list_list[i - 1][0].bbox[0]:
                pass
            assert char_list_list[i][0].bbox[0] >= char_list_list[i-1][0].bbox[0]

    ret_char_list = []
    for i, idx in enumerate(idx_list):
        tmp_char_list = char_list_list[idx]
        ret_char_list.extend(tmp_char_list)
        if i != len(idx_list) - 1:
            ret_char_list.append(LTAnno(' '))

    return ret_char_list


def re_group_char_list_merge_isolated_digit(char_list_in, font):
    char_list_list = get_char_list_list(char_list_in)
    word_list = []
    for word_char_list in char_list_list:
        word_list.append(char_list2str(word_char_list))
    if MERGE_ISOLATED_DIGIT:
        while True:
            merge_pos = None
            for i in range(len(word_list) - 1):
                next_first_latex_val = get_latex_val_of_lt_char(
                    char_list_list[i + 1][0], font)
                prev_last_latex_val = get_latex_val_of_lt_char(
                    char_list_list[i][-1], font)
                if word_list[i].isdigit() and \
                        (is_bin_op_latex_val(next_first_latex_val) or is_rel_latex_val(next_first_latex_val)):
                    merge_pos = i
                    break
                elif word_list[i + 1].isdigit() and \
                        (is_bin_op_latex_val(prev_last_latex_val) or is_rel_latex_val(prev_last_latex_val)):
                    merge_pos = i
                    break
                else:
                    pass
            if merge_pos is None:
                break
            # process
            new_char_list_list = []
            i = 0
            while i < len(char_list_list):
                if i == merge_pos:
                    new_char_list_list.append(char_list_list[i])
                    new_char_list_list[-1].extend(char_list_list[i + 1])
                    i += 1
                else:
                    new_char_list_list.append(char_list_list[i])
                i += 1

            char_list_list = new_char_list_list
            word_list = []
            for word_char_list in char_list_list:
                word_list.append(char_list2str(word_char_list))

    return char_list_list2char_list(char_list_list)


def re_group_char_list_split(char_list_in):
    """
    split the unmatched parenthesis

    :param char_list_in:
    :return:
    """
    char_list_list = get_char_list_list(char_list_in)
    word_list = []
    for word_char_list in char_list_list:
        word_list.append(char_list2str(word_char_list))

    if SPLIT_UNPAIRED_PARENTHESIS:
        while True:
            do_split = False
            new_char_list_list = []
            for i in range(len(char_list_list)):
                if word_list[i].count('(') == 1 and \
                        word_list[i].count(')') == 0 and \
                        word_list[i][0] == '(' and \
                        len(word_list[i]) > 1:
                    new_char_list_list.append([char_list_list[i][0]])
                    new_char_list_list.append(char_list_list[i][1:])
                    do_split = True
                elif word_list[i].count('(') == 0 and \
                        word_list[i].count(')') == 1 and \
                        word_list[i][-1] == ')' and \
                        len(word_list[i]) > 1:
                    new_char_list_list.append(char_list_list[i][0:-1])
                    new_char_list_list.append([char_list_list[i][-1]])
                    do_split = True
                else:
                    new_char_list_list.append(char_list_list[i])

            if do_split:
                char_list_list = new_char_list_list
                word_list = []
                for word_char_list in char_list_list:
                    word_list.append(char_list2str(word_char_list))
            else:
                break
    return char_list_list2char_list(char_list_list)


def re_group_ending_punct(char_list_in, font):
    """
    split the last punct from the words, usuallly not part of word or ME

    :param char_list_in:
    :param font:
    :return:
    """
    char_list_list = get_char_list_list(char_list_in)
    new_char_list_list = []
    for char_list in char_list_list:
        latex_val = get_latex_val_of_lt_char(char_list[-1], font)
        if latex_val in [',', '.', ';', ":", 'comma', 'period', 'colon']:
            new_char_list_list.append(char_list[:-1])
            new_char_list_list.append([char_list[-1]])
        else:
            new_char_list_list.append(char_list)

    return char_list_list2char_list(new_char_list_list)


def re_group_char_list_merge_unmatched_parenthesis(char_list_in, font):
    """
    NOTE:

    :param char_list_in:
    :param font:
    :return:
    """
    char_list_list = get_char_list_list(char_list_in)
    word_list = []
    for word_char_list in char_list_list:
        word_list.append(char_list2str(word_char_list))

    while True:
        merge_unmatched = False
        new_char_list_list = []
        i = 0
        while i < len(char_list_list):
            if i+1 < len(char_list_list) and \
                    word_list[i].count('(') == 1 and \
                    word_list[i].count(')') == 0 and \
                    word_list[i+1].count(')') == 1:
                new_char_list_list.append(char_list_list[i])
                new_char_list_list[-1].extend(char_list_list[i+1])
                i += 2
                merge_unmatched = True
            else:
                new_char_list_list.append(char_list_list[i])
                i += 1

        if not merge_unmatched:
            break
        else:
            char_list_list = new_char_list_list
            word_list = []
            for word_char_list in char_list_list:
                word_list.append(char_list2str(word_char_list))

    return char_list_list2char_list(char_list_list)


def all_cap(char_list):

    for char in char_list:
        if char.get_text() not in string.uppercase:
            return False
    return True


def re_group_merge_cap(char_list_in):
    """

    :param char_list_in:
    :return:
    """
    #print char_list2str(char_list_in)

    char_list_list = get_char_list_list(char_list_in)
    i = 0
    processed_char_list_list = []
    while i < len(char_list_list):
        merge_with_next = False
        if i < len(char_list_list)-1 and all_cap(char_list_list[i]):
            if char_list_list[i+1][0].get_text() in string.uppercase:
                merge_with_next = True

        if merge_with_next:
            tmp_list = list(char_list_list[i])
            tmp_list.extend(char_list_list[i+1])
            processed_char_list_list.append(tmp_list)
            i += 2
        else:
            processed_char_list_list.append(char_list_list[i])
            i += 1

        #if len(tmp_list) > 0:
        #    processed_char_list_list.append(tmp_list)
    #tmp_char_list = char_list_list2char_list(processed_char_list_list)
    #print char_list2str(tmp_char_list)

    return char_list_list2char_list(processed_char_list_list)


def re_group_char_list(char_list_in, font, debug=False):
    """
    remove or insert LTAnno when necessary

    :param char_list:
    :return:
    """
    if debug:
        print "Input ", char_list2str(char_list_in)
    # regroup the unmatched parenthesis
    # do this first, otherwise, might be splited again by the split func
    char_list_in = re_group_char_list_merge_unmatched_parenthesis(char_list_in, font)
    if debug:
        print "After parenthesis", char_list2str(char_list_in)

    char_list_in = re_group_ending_punct(char_list_in, font)
    if debug:
        print "After Punct", char_list2str(char_list_in)

    # based on the binary operator
    char_list_in = re_group_char_list_merge_isolated_digit(char_list_in, font)
    if debug:
        print "After isolated digit", char_list2str(char_list_in)

    char_list_in = re_group_char_list_split(char_list_in)
    if debug:
        print "After isolated digit", char_list2str(char_list_in)

    # merge oversplit captalized
    char_list_in = re_group_merge_cap(char_list_in)
    if debug:
        print "After cap", char_list2str(char_list_in)

    # TODO, binary relation/operator merger


    return char_list_in


def re_group_char_list_seg(char_list_in, fontname2space):
    """
    segment

    :param fontname2space: from pdfbox, about the space size
    :param char_list_in: the list of char to insert LTAnno
    :return:
    """
    char_list_in = [c for c in char_list_in if isinstance(c, LTChar)]

    return_char_list = []
    for cid, char in enumerate(char_list_in):
        is_space = False
        if isinstance(char, LTChar) and char.get_text() in [' ', 'space']:
            is_space = True
        if is_space:
            return_char_list.append(char)  # NOTE, still keep the space char for later analysis
            return_char_list.append(LTAnno(' '))
            continue

        return_char_list.append(char)

        # if the space with next char is larger than 0.5 of the previous char, add space
        if cid != len(char_list_in) - 1:
            #half_width = BBox(char.bbox).width() / 2
            next_bbox = get_adj_bbox(char_list_in[cid+1])
            cur_bbox = get_adj_bbox(char_list_in[cid])
            space_size = get_space_size(char, fontname2space)
            # TODO, note that it's only a pre-merging.
            # the sub exp will be merged based on the word from pdfbox
            thres = space_size * SPACE_THRES_RATIO

            if next_bbox.left() - cur_bbox.right() > thres:
                #if char_list_in[cid+1].bbox[0] - char_list_in[cid].bbox[2] :
                return_char_list.append(LTAnno(' '))

    # remove extra ltaano
    final_return_char_list = []
    for char in return_char_list:
        if len(final_return_char_list) > 0 and \
                isinstance(char, LTAnno) and \
                isinstance(final_return_char_list[-1], LTAnno):
            continue
        final_return_char_list.append(char)

    post_process_char_list = re_group_char_list(final_return_char_list, None)
    return post_process_char_list


def insert_ltanno_line(char_list, thres=None):
    """
    Based on the threshold to insert space among chars

    :param char_list:
    :param thres:
    :return:
    """
    if thres is None:
        # just use 0.5 of the char width as the threshold
        width_list = [c.bbox[2]-c.bbox[0] for c in char_list]
        thres = 0.5 * np.median(width_list)
    char_list.sort(key=lambda c: c.bbox[0])
    if len(char_list) == 0:
        return []
    new_char_list = list()
    new_char_list.append(char_list[0])
    for i in range(1, len(char_list)):
        if char_list[i].bbox[0] - char_list[i-1].bbox[2] > thres:
            new_char_list.append(LTAnno(' '))
        new_char_list.append(char_list[i])
    return new_char_list


def get_space_size(char, fontname2space):
    """
    This is called for a pre-merging of chars as word
     A further merging will be conducted later

    estimated the space for the char,
    This is not accurate, PDF specification is required.

    :param char:
    :param fontname2space:
    :return:
    """
    assert isinstance(char, LTChar)
    if char.fontname in fontname2space:
        tmp_val = fontname2space[char.fontname]
    else:
        tmp_val = np.mean(fontname2space.values())

    # if too large, just use the char size
    char_width = char.bbox[2]-char.bbox[0]
    if tmp_val > char_width:
        tmp_val = np.min(fontname2space.values())
    return tmp_val


def get_adj_bbox(char):
    """
    Want to adjust the bounding box based on
     whether the char is italic,
     This is not accurate

    36, 150, 154
    In the past, want to adjust based on whether italic or not

    :param char:
    :return:
    """
    assert isinstance(char, LTChar)
    return BBox(char.bbox)

    import re
    if re.search(r"italic", char.fontname, re.I):
        tmp_bbox = BBox(char.bbox)
        h_cen = tmp_bbox.h_center()
        tmp_width = tmp_bbox.width() - tmp_bbox.height() * 36.0 / 150
        tmp_bbox.set_left(h_cen - tmp_width / 2)
        tmp_bbox.set_right(h_cen + tmp_width / 2)
        return tmp_bbox
    else:
        return BBox(char.bbox)


if __name__ == "__main__":
    pass