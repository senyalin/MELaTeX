"""
the 2 here has two meansing:
 * version 2
 * split the HC into two parts, rather than three parts in the first version.

identify, and evaluation.
"""
from pdfxml.InftyCDB.data_portal.data_portal import get_cid2me_idx
from pdfxml.me_layout.layout_configuration.script_config_util import is_same_level
from pdfxml.me_layout.layout_configuration.script_config_inftycdb import load_sc_for_infty

debug = False

bad_count = 0
good_count = 0


def get_split_idx(elem_list):
    """
    get the element with the largest height
    less likely to be the SUP/SUB of other elements

    :return:
    """
    if len(elem_list) <= 1:
        raise Exception("should have more than 10 elements")

    split_idx = len(elem_list)-1  # should not be the first elements
    for i, elem in enumerate(elem_list):
        if i == 0:
            continue
        if elem.get_adjusted_bbox().height() > elem_list[split_idx].get_adjusted_bbox().height():
            split_idx = i

    if debug:
        cid2me_idx = get_cid2me_idx()

        # get the element of the split
        # get the me_idx, and recover the script config,
        # and check whether the first element and the split position in the same level
        head_elem = elem_list[0].attacher_object()
        split_elem = elem_list[split_idx].attacher_object()
        head_cid = head_elem.get_info("cid")
        split_cid = split_elem.get_info("cid")
        me_idx = cid2me_idx[split_cid]
        sc = load_sc_for_infty(me_idx)  # load the script config
        rel_list = sc.get_rel_list(head_cid, split_cid) # check whether the two are at the same level.
        same_level = is_same_level(rel_list)
        # only_one_child or no child
        # for the element at the split position, have at most one children
        if not same_level:
            print 'bad selection'
            global bad_count
            bad_count += 1
        else:
            global good_count
            good_count += 1

        print 'good/bad, {}/{}'.format(good_count, bad_count)

    return split_idx


if __name__ == "__main__":
    #inspect_split()
    print 'good/bad, {}/{}'.format(good_count, bad_count)
