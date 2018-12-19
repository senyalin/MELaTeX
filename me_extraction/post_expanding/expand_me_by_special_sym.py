"""

"""
from pdfxml.me_extraction.post_expanding.expanding_resources import \
    expand_left_right_list, expand_left_sym_list, expand_right_sym_list
from pdfxml.pdf_util.word_seg_process import char_list2char_list_list
from pdfxml.pdf_util.char_process import get_latex_val_of_lt_char


def could_expand_left(word):
    """

    :param word: list of LTChar
    :return:
    """
    if len(word) == 0:
        return False
    latex_val = get_latex_val_of_lt_char(word[0])
    return latex_val in expand_left_right_list or \
        latex_val in expand_left_sym_list


def could_expand_right(word):
    """

    :param word:
    :return:
    """
    if len(word) == 0:
        return False
    latex_val = get_latex_val_of_lt_char(word[0])
    return latex_val in expand_left_right_list or \
        latex_val in expand_right_sym_list


def get_me_nscs_by_expand_special_sym(line):
    """

    :param line:
    :return:
    """
    expand_me_nscs_list = []
    word_list = char_list2char_list_list(line)
    for i, word in enumerate(word_list):
        # try expand left
        if could_expand_left(word) and i > 0:
            expand_me_nscs_list.append(word_list[i-1])
        # try expand right
        if could_expand_right(word) and i < len(word_list)-1:
            expand_me_nscs_list.append(word_list[i+1])
    return expand_me_nscs_list

