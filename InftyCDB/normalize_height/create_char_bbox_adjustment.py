"""
local notation table:
    char_info: show in the data_portal

"""
import os
import numpy as np
from pdfxml.file_util import load_serialization, dump_serialization, load_general, dump_general
from pdfxml.path_util import infty_cdb_folder, SHARED_FOLDER
from pdfxml.pdf_util.layout_util import get_y_center, get_width
from pdfxml.InftyCDB.data_portal.infty_cdb_me import construct_hierarchy_by_me_idx
from pdfxml.InftyCDB.data_portal.data_portal import get_code2name, get_me_idx_list
from pdfxml.InftyCDB.normalize_height.line_properties import lower_exist, \
    get_lower_line, upper_exist, get_upper_line
from pdfxml.InftyCDB.infty_cdb_util import get_glyph_type


# code2name = get_code2name()


def get_baseline_y_ratio(char_info, base_line):
    """

    :param char_info:
    :param base_line: a scalar value
    :return:
    """
    return (base_line - char_info['bbox'][1]) / \
           (char_info['bbox'][3] - char_info['bbox'][1])


def get_lower_ratio(char_info, lower_line):
    """
    given the

    :param char_info: a dict of char information, mainly use the bbox here
    :param lower_line: a scalar value for vertical position
    :return: a scalar value showing how to adjust the lower bound of bbox
    """
    r = (char_info['bbox'][1] - lower_line) / (char_info['bbox'][3]-char_info['bbox'][1])
    if np.isnan(r):
        print char_info
        print lower_line
        raise Exception("meet nan value")
    return r


def get_upper_ratio(cinfo, upper_line):
    r = (upper_line - cinfo['bbox'][3]) / (cinfo['bbox'][3]-cinfo['bbox'][1])
    if np.isnan(r):
        print cinfo
        print upper_line
        raise Exception("meet nan value")
    return r


def get_lower_ratio_hor(cinfo, lower_line):
    """
    using the horizontal width, rather than the vertical height
    because the height might be very thin
    """
    # get mean in vertical direction
    y_cen = get_y_center(cinfo['bbox'])
    return (y_cen - lower_line) / get_width(cinfo['bbox'])


def get_upper_ratio_hor(cinfo, upper_line):
    """
    given the upper line and the cinfo,
    calculate the vertical difference of upper boundary w.r.t. the vertical center,
    with respect to the width of the current char.

    :param cinfo:
    :param upper_line:
    :return:
    """
    y_cen = get_y_center(cinfo['bbox'])
    return (upper_line - y_cen) / get_width(cinfo['bbox'])


def print_line(cidlist, cid2info):
    """
    print out the char names given the list of ids,
    the char infor in cid2info dict

    :param cidlist:
    :param cid2info:
    :return:
    """
    for cid in cidlist:
        print cid2info[cid]['name'].strip(),
    print ''


def get_char2extend_for_one(me_idx, debug=False):
    """
    based on the horizontal grouping from construct_hierarchy
    try to make assessment on the correction of the bbox

    :param me_idx: the idx of ME
    :type me_idx: int
    :param debug:
    :return: a dict, code 2 upper_list and code 2 lower_list
        'code2upper_ratio': use height to adjust upper
        'code2upper_ratio_hor': use the width to adjust upper, because the error rate for the flat sign such as minus is hard to estimate.
        'code2lower_ratio': use height to adjust lower
        'code2lower_ratio_hor': use the width to adjust lower
    """
    code2name = get_code2name()

    cached_path = "{}/char2extend_ratio/{}.pkl".format(infty_cdb_folder, me_idx)
    if not debug and os.path.isfile(cached_path):
        # if not debug and the file exist
        return load_serialization(cached_path)

    code2upper_ratio, code2upper_ratio_hor, \
        code2lower_ratio, code2lower_ratio_hor = {}, {}, {}, {}
    res = {
        'code2upper_ratio': code2upper_ratio, 'code2upper_ratio_hor': code2upper_ratio_hor,
        'code2lower_ratio': code2lower_ratio, 'code2lower_ratio_hor': code2lower_ratio_hor
    }

    def update_dict(d, k, v):
        if not d.has_key(k):
            d[k] = []
        d[k].append(v)

    # change to inftyCDBME
    try:
        struct_info = construct_hierarchy_by_me_idx(me_idx)
    except Exception as e:
        print "failed for me_idx {} {}".format(me_idx, str(e))
        return res

    cid2info = struct_info.cid2chars
    for group in struct_info.hor_groups:

        # each group is a list of cid
        if upper_exist(group, cid2info):
            upper_line = get_upper_line(group, cid2info)
            if debug:
                print 'ascender_line: {}'.format(upper_line)
                print_line(group, cid2info)

            for cid in group:
                r = get_upper_ratio(cid2info[cid], upper_line)
                r_hor = get_upper_ratio_hor(cid2info[cid], upper_line)
                update_dict(code2upper_ratio, cid2info[cid]['code'], r)
                update_dict(code2upper_ratio_hor, cid2info[cid]['code'], r_hor)
                if debug:
                    print cid, code2name[cid2info[cid]['code']], \
                        "code2upper_ratio", r, \
                        "code2upper_ratio_hor", r_hor

        if lower_exist(group, cid2info):
            lower_line = get_lower_line(group, cid2info)
            if debug:
                print 'descender_line: {}'.format(lower_line)
                print_line(group, cid2info)

            for cid in group:
                r = get_lower_ratio(cid2info[cid], lower_line)
                r_hor = get_lower_ratio_hor(cid2info[cid], lower_line)
                update_dict(code2lower_ratio, cid2info[cid]['code'], r)
                update_dict(code2lower_ratio_hor, cid2info[cid]['code'], r_hor)
                if debug:
                    print cid, code2name[cid2info[cid]['code']], \
                        "code2lower_ratio", r, \
                        "code2lower_ratio_hor", r_hor

    dump_serialization(res, cached_path)
    return res


# TODO, char2extend_ratio, for each ME, estimate the adjusted ascender/descender
def get_me_idx_list_with_adjustment():
    """
    each file in this folder corresponds to one ME,
    The value is about how to normalized each character, for detail, please see `get_char2extend_for_one`

    :return: list of index of ME
    :rtype: list[int]
    """
    print "PLEASE stop from using this as the enumeration of all me_idx, some other ME, although without adjustment, could still be evaluated"

    ratio_folder = "{}/char2extend_ratio".format(infty_cdb_folder)
    me_idx_list = []
    for file_name in os.listdir(ratio_folder):
        me_idx = int(file_name[:-4])
        me_idx_list.append(me_idx)
    return me_idx_list


def create_all_adjustment_ratio():
    """
    This is code level adjustment, which is a very refined level.

    :return:
    """
    cache_path = "{}/tmp/all_adjustment_ratio_code_level.json".format(infty_cdb_folder)
    if os.path.isfile(cache_path):
        return load_general(cache_path)

    total = {
        'code2upper_ratio': {},
        'code2upper_ratio_hor': {},
        'code2lower_ratio': {},
        'code2lower_ratio_hor': {}
    }

    def update(info_dict):
        for k in total.keys():
            c2rlist = info_dict[k]
            for c, rlist in c2rlist.items():  # code to list of ratio values
                if c not in total[k]:
                    total[k][c] = []
                total[k][c].extend(rlist)

    me_idx_list = get_me_idx_list()

    #me_idx_list = get_me_idx_list_with_adjustment()
    for n, me_idx in enumerate(me_idx_list):
        if n % 100 == 0:
            print "done loading {} files".format(n)
        adjust_dict = get_char2extend_for_one(me_idx)
        update(adjust_dict)

    dump_general(total, cache_path)
    return total


def unify_all_adjustment_ratio():
    """
    collect the adjustment from all ME, to create adjustment parameter

    :return:
    """
    return create_all_adjustment_ratio()


def unify_glyph_type_adjustment_ratio():
    """
    In comparison with `create_all_adjustment_ratio`,
    this is a marginal version with each code mapping to the glyph type

    :return: from glyph_type to list of adjustment ratio
    """
    from pdfxml.path_util import PROJECT_FOLDER
    #cache_path = "{}/tmp/all_adjustment_ratio_glyph_type_level.pkl".format(infty_cdb_folder)
    cache_path = "{}/InftyCDB-1/cache_data/all_adjustment_ratio_glyph_type_level.json".format(
        SHARED_FOLDER)

    if os.path.isfile(cache_path):
        return load_general(cache_path)

    code2name = get_code2name()

    total = unify_all_adjustment_ratio()
    # gt is short for glyph_type
    # the code here is the glyph type
    gt_dict = {
        'code2upper_ratio': {},
        'code2upper_ratio_hor': {},
        'code2lower_ratio': {},
        'code2lower_ratio_hor': {}
    }

    # NOTE: This is what I am looking for to ajdust by group
    for adjustment_type in total.keys():
        c2rlist = total[adjustment_type]
        for c, rlist in c2rlist.items():
            gt = get_glyph_type(code2name[c])
            if gt not in gt_dict[adjustment_type]:
                gt_dict[adjustment_type][gt] = []
            gt_dict[adjustment_type][gt].extend(rlist)

    dump_general(gt_dict, cache_path)
    return gt_dict


def get_latex2adjustment_ratio_list():
    from pdfxml.InftyCDB.name2latex import name2latex
    cache_path = "{}/InftyCDB-1/cache_data/all_adjustment_ratio_list_latex.json".format(SHARED_FOLDER)
    if os.path.isfile(cache_path):
        return load_general(cache_path)

    code2name = get_code2name()
    gt_dict = {
        'code2upper_ratio': {},
        'code2upper_ratio_hor': {},
        'code2lower_ratio': {},
        'code2lower_ratio_hor': {}
    }

    total = unify_all_adjustment_ratio()
    for adjustment_type in total.keys():
        c2rlist = total[adjustment_type]
        for c, rlist in c2rlist.items():
            latex_val = name2latex[code2name[c]]
            if latex_val not in gt_dict[adjustment_type]:
                gt_dict[adjustment_type][latex_val] = []
            gt_dict[adjustment_type][latex_val].extend(rlist)
    dump_general(gt_dict, cache_path)

    return gt_dict


if __name__ == "__main__":
    get_latex2adjustment_ratio_list()
