"""
To enable fast processing, split the whole file based on the ME unit
"""
import os
from pdfxml.file_util import load_serialization, dump_serialization
from pdfxml.path_util import infty_cdb_folder
from pdfxml.InftyCDB.data_portal.data_portal import load_char_map


def get_me_idx2chars():
    """
    create map from file name to list of chars

    :return: string_wx of fname mapped to list of chars
    :rtype: dict[string_wx, list[dict]]
    """
    chars = load_char_map().values()
    # split by fname
    me_idx2chars = {}
    for char in chars:
        # split by check overlapping
        me_idx = char['me_idx']
        if me_idx not in me_idx2chars:
            me_idx2chars[me_idx] = []
        me_idx2chars[me_idx].append(char)
    return me_idx2chars


def get_cached_chars_path_by_me_idx(me_idx):
    cached_path = "{}/crop_chars/me_idx_{}.pkl".format(infty_cdb_folder, me_idx)
    return cached_path


def batch_split_chars_by_me_idx():
    from pdfxml.file_util import test_folder_exist_for_file_path
    me_idx2chars = get_me_idx2chars()
    # load all first
    for me_idx, chars in me_idx2chars.items():
        cached_path = get_cached_chars_path_by_me_idx(me_idx)
        test_folder_exist_for_file_path(cached_path)
        if os.path.isfile(cached_path):
            continue
        dump_serialization(chars, cached_path)


def load_chars_by_me_idx(me_idx):
    """
    given an integer of me idx, return the related chars

    :param me_idx:
    :return: list[dict]
    """
    cached_path = get_cached_chars_path_by_me_idx(me_idx)
    if not os.path.isfile(cached_path):
        batch_split_chars_by_me_idx()
    elem_list = load_serialization(cached_path)
    # NOTE, extra processing for the path of the radical line

    # check the parent not in the list, if only one, change its parent as -1 and the relation as TOP
    cid_list = [elem['cid'] for elem in elem_list]
    cid_list_with_bad_pid = []
    for elem in elem_list:
        if elem['pid'] != -1 and elem['pid'] not in cid_list:
            cid_list_with_bad_pid.append(elem['cid'])
    if len(cid_list_with_bad_pid) == 0:
        return elem_list
    elif len(cid_list_with_bad_pid) == 1:
        # update the one
        the_idx = -1
        for i, elem in enumerate(elem_list):
            if elem['pid'] != -1 and elem['pid'] not in cid_list:
                the_idx = i
        elem_list[the_idx]['pid'] = -1
        elem_list[the_idx]['relation'] = "TOP"
        return elem_list
    else:
        raise Exception("more than two elements")


if __name__ == "__main__":
    batch_split_chars_by_me_idx()
