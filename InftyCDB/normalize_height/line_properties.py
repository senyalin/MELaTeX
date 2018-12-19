import numpy as np
from pdfxml.InftyCDB.infty_cdb_util import get_glyph_type


def height_adjustable_gt(idx, cid2info):
    """
    In the regular glyph type

    :param idx:
    :param cid2info:
    :return:
    """
    if idx not in cid2info:
        return False
    gt = get_glyph_type(cid2info[idx]['name'])
    return gt in ["y", "xy", "yz", "xyz", "hxy", "hxyz"]


def baseline_char_exist(idx_list, cid2info):
    """
    x is the ascender part,
    y is the center part,
    z is the descender part

    just need to collect the center part so that we have the baseline estimated.

    :param idx_list: char id in the Infty CDB data
    :param cid2info:
    :return:
    """
    for idx in idx_list:
        gt = get_glyph_type(cid2info[idx]['name'])
        if gt in ['y', 'xy']:
            return True
    return False


def get_base_line(idx_list, cid2info):
    """
    Assuming there is a baseline, and calculated it

    :param idx_list:
    :param cid2info:
    :return: scalar value indicating the vertical position
    """
    base_list = []
    for idx in idx_list:
        gt = get_glyph_type(cid2info[idx]['name'])
        if gt in ['y', 'xy']:
            base_list.append(cid2info[idx]['bbox'][1])
    base_line = np.median(base_list)
    return base_line


def check_x_exist(char_name_list):
    """
    check whether x part exist in the list of chars

    :param char_name_list: list of string_wx of char name
    :return: bool
    """
    for char_name in char_name_list:
        if get_glyph_type(char_name) in ['xy', 'xyz']:
            return True
    return False


def check_z_exist(char_name_list):
    """
    check whether the z part exist

    :param char_name_list: list of string_wx of char name
    :return: bool
    """
    for char_name in char_name_list:
        if get_glyph_type(char_name)in ['yz', 'xyz', 'hxyz']:
            return True
    return False


def is_base(char_name):
    return get_glyph_type(char_name) in ['y', 'xy', 'hxy']


def is_lower(c):
    return get_glyph_type(c).count('z') > 0


def is_upper(c):
    gt = get_glyph_type(c)
    return gt in ['xy', 'xyz']


def lower_exist(idx_list, cid2info):
    """

    :param idx_list: list of cid from InftyCDB dataset
    :param cid2info:
    :return:
    """
    return check_z_exist([cid2info[idx]['name'] for idx in idx_list])


def get_lower_line(idx_list, cid2info):
    ll = []
    for idx in idx_list:
        n = cid2info[idx]['name']
        if is_lower(n):
            ll.append(cid2info[idx]['bbox'][1])
    return np.median(ll)


def upper_exist(idx_list, cid2info):
    """

    :param idx_list: list of idx from InftyCDB dataset
    :param cid2info:
    :return:
    """
    return check_x_exist([cid2info[idx]['name'] for idx in idx_list])


def get_upper_line(idx_list, cid2info):
    """
    given a list of idx, get the adjusted upper line

    :param idx_list:
    :param cid2info:
    :return: None if could not calculate the upper line
    """
    if not upper_exist(idx_list, cid2info):
        return None
    upper_line_list = [
        cid2info[idx]['bbox'][3] for idx in idx_list if is_upper(cid2info[idx]['name'])
    ]
    return np.median(upper_line_list)