"""
This processing will identify the SUP and SUB in MEHSSGroup
 based on the following procedures:
 1.sort from left to right

The correctness will depend on the following assumptions:
***

enable_boundary_by_centerline_for_ss

"""

import pdfxml.me_layout.me_layout_config as me_layout_config
from pdfxml.me_layout.me_group.hor_me_group import MEHorGroup
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.vertical_me_group import MESupSubGroup, MEBindVarGroup, MEFractionGroup, MEAccentGroup
from pdfxml.me_layout.me_group.enclosed_me_group import MERadicalGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath, MEHSSGroup, MEHorSupOrSubGroup
from pdfxml.me_layout.char_adjust_bbox_core import center_line_overlapping_checking


def sup_sub_checking(me_group_base, me_group1, me_group2, debug=False):
    """
    me_group1 and me_group2 are on the right of center of me_group_base
    me_group1 and me_group2 both overlap with me_group_base vertically
    me_group1 and me_group2 horizontal overlapping (which might not be true)
    me_group1 and me_group2 dont overlap vertically

    Condition to raise exception.

    :param me_group_base:
    :type me_group_base: MEGroup
    :param me_group1:
    :type me_group1: MEGroup
    :param me_group2:
    :type me_group2: MEGroup
    :return:
    """
    if debug:
        print "chekcing", me_group_base, me_group1, me_group2
        print me_group_base.get_adjusted_bbox()
        print me_group1.get_adjusted_bbox()
        print me_group2.get_adjusted_bbox()

    # both should not be puncutation
    from pdfxml.me_taxonomy.latex.latex_punct import latex_punct_list
    baseline_symbol_1 = me_group1.get_baseline_symbol()
    if baseline_symbol_1 is None:
        return False
    if baseline_symbol_1.latex_val in latex_punct_list:
        return False

    baseline_symbol_2 = me_group2.get_baseline_symbol()
    if baseline_symbol_2 is None:
        return False
    if baseline_symbol_2.latex_val in latex_punct_list:
        return False


    # on the right of base center
    if me_group1.left() < me_group_base.get_adjusted_bbox().h_center():
        return False
    if me_group2.left() < me_group_base.get_adjusted_bbox().h_center():
        return False

    # size checking
    if me_group1.get_adjusted_bbox().height() > me_group_base.get_adjusted_bbox().height():
        return False
    if me_group2.get_adjusted_bbox().height() > me_group_base.get_adjusted_bbox().height():
        return False

    # vertical overlap with base

    #me_group1.get_adjusted_bbox()
    #me_group_base
    # if not me_group1.v_overlap(me_group_base.get_adjusted_bbox()):
    #    return False
    # if not me_group2.v_overlap(me_group_base.get_adjusted_bbox()):
    #    return False

    if not me_group1.get_tight_bbox().v_overlap(me_group_base.get_adjusted_bbox()):
        return False
    if not me_group2.get_tight_bbox().v_overlap(me_group_base.get_adjusted_bbox()):
        return False

    # should horizontal overlap
    #if not me_group1.h_overlap(me_group2):
    #    return False
    # remove this condition as some big integral is very long,
    # causing the first element of sub/sup not overlap horizontally

    # should not vertically overlap
    if me_group1.v_overlap(me_group2):
        return False

    # do extra center line analysis between base and sup/sub
    # the more complex the checking is, the later it should be put
    if center_line_overlapping_checking(me_group_base, me_group1):
        return False
    if center_line_overlapping_checking(me_group_base, me_group2):
        return False

    if center_line_overlapping_checking(me_group1, me_group_base):
        return False
    if center_line_overlapping_checking(me_group2, me_group_base):
        return False

    if isinstance(me_group_base, MESymbolGroup):
        if me_group_base.me_symbol.latex_val in ['(', '{', '[']:
            return False

    return True


def recursive_organize_subandsup(mg):
    """
    TODO, there is some logic error that
    before calling the current function

    :param hss_group:
    :return:
    """
    # should be converted to HSS already
    assert not isinstance(mg, UnorganizedGroupPath)
    if isinstance(mg, MEAccentGroup):
        ":type ugp: MEHatGroup"
        mg.me_group = recursive_organize_subandsup(mg.me_group)
        return mg
    elif isinstance(mg, MERadicalGroup):
        ":type ugp: MESqrtGroup"
        mg.me_group = recursive_organize_subandsup(mg.me_group)
        return mg
    elif isinstance(mg, MEFractionGroup):
        mg.down_me_group = recursive_organize_subandsup(mg.down_me_group)
        mg.up_me_group = recursive_organize_subandsup(mg.up_me_group)
        return mg
    elif isinstance(mg, MEBindVarGroup):
        mg.down_me_group = recursive_organize_subandsup(mg.down_me_group)
        mg.up_me_group = recursive_organize_subandsup(mg.up_me_group)
        return mg
    elif isinstance(mg, MESymbolGroup):
        return mg
    elif isinstance(mg, MEHSSGroup):
        mg = organize_subandsup_in_hss(mg)
        new_me_groups = [
            recursive_organize_subandsup(tmp_mg_group)
            for tmp_mg_group in mg.me_groups
        ]
        mg.me_groups = new_me_groups

        return mg
    elif isinstance(mg, MESupSubGroup):
        # bug of missing this part.
        mg.base_me_group = recursive_organize_subandsup(mg.base_me_group)
        mg.sub_me_group = recursive_organize_subandsup(mg.sub_me_group)
        mg.sup_me_group = recursive_organize_subandsup(mg.sup_me_group)
        return mg
    elif isinstance(mg, MEHorSupOrSubGroup):
        return mg
    elif isinstance(mg, EmptyGroup):
        return mg
    elif isinstance(mg, MEHorGroup):
        for tmp_mg in mg.me_groups:
            assert isinstance(tmp_mg, MESymbolGroup)
        return mg
    else:
        print type(mg)
        raise Exception("Unknown type")


def get_sup_sub_base_idx(hss_group):
    """

    :param hss_group:
    :return:
    """
    sup_sub_base_idx = -1
    for i in range(len(hss_group.me_groups) - 2):
        # must have at least two me_groups on the right
        check_ok = sup_sub_checking(
            hss_group.me_groups[i],
            hss_group.me_groups[i + 1],
            hss_group.me_groups[i + 2])
        if check_ok:
            sup_sub_base_idx = i
            break
    return sup_sub_base_idx


def organize_subandsup_in_hss_center_line(hss_group, debug=False):
    """
    1. get the base char
    2. find the following char that lies in the center range as the stop
    3. every with vertical center above the centerline as superscript
        and below as the subscript

    :param hss_group:
    :param debug:
    :return:
    """
    pass


def organize_subandsup_in_hss(hss_group, debug=False):
    """
    consider this case 1_{2_3^4}^{5_6^7}
    This indicate the necessity to recursively do it?

    The recursively way is first identify the first layer of sup & sub
    create MEHSSGroup for sub and sup,
    call organize_subandsup_in_hss on these two

    After the processing only hor or sub/sup, no sub/sup at the same time

    :param hss_group: the group unorganized, but want to identify the both sup&sub part
    :type hss_group: MEHSSGroup
    :return:
    :rtype: MEHorSupOrSubGroup
    """
    assert isinstance(hss_group, MEHSSGroup)

    # first recursively process each one
    # otherwise, the inner hss under hss will not be processed.
    hss_group.me_groups = [recursive_organize_subandsup(me_group) for me_group in hss_group.me_groups]

    hss_group.me_groups.sort(key=lambda me_group: me_group.left())
    while True:
        sup_sub_base_idx = get_sup_sub_base_idx(hss_group)
        if sup_sub_base_idx == -1:  # could not find a one
            break

        me_group_base = hss_group.me_groups[sup_sub_base_idx]

        # TODO, might want to just use the center line criteria for such split

        me_group_sup = hss_group.me_groups[sup_sub_base_idx + 1]
        ":type: MEGroup"
        me_group_sub = hss_group.me_groups[sup_sub_base_idx + 2]
        ":type: MEGroup"
        if me_group_sup.tight_bottom() < me_group_sub.tight_top():  # swap if reversed
            me_group_sup, me_group_sub = me_group_sub, me_group_sup

        # TODO, the logic here is not very good
        # 1. for the case of 28001911, the under component of other element is also included here
        # 2. sometimes, the equal sign followed will only overlap with one of the sup and sub, causing error in identification.
        # one stop rule of expanding is if the horzontal distance is larger than 2 of the average size

        # group the sup and sub
        # keep expanding if only overlap with one of them or not overlapping
        # if overlap with both, stop
        i = sup_sub_base_idx+1
        sup_group_idx_list = []
        sub_group_idx_list = []

        sup_right_bound = me_group_sup.right()
        sub_right_bound = me_group_sub.right()

        total_char_num = 2
        total_char_width = me_group_sup.width()+ me_group_sub.width()
        while i < len(hss_group.me_groups):

            # TODO
            sup_overlap = me_group_sup.v_overlap(hss_group.me_groups[i])
            sub_overlap = me_group_sub.v_overlap(hss_group.me_groups[i])
            if sup_overlap and sub_overlap:  # stop condition
                break

            if me_layout_config.enable_boundary_by_centerline_for_ss:
                # TODO, checking based on the center line analysis
                # get the normalized center and check the center line
                if center_line_overlapping_checking(me_group_base, hss_group.me_groups[i]):
                    break

            if sup_overlap:
                # if empty, then just add
                if len(sup_group_idx_list) == 0:
                    sup_group_idx_list.append(i)
                else:
                    hor_diff = hss_group.me_groups[i].left() - sup_right_bound
                    if hor_diff < 2.0 * total_char_width / total_char_num:
                        sup_group_idx_list.append(i)
                        sup_right_bound = hss_group.me_groups[i].right()
                        total_char_width += hss_group.me_groups[i].width()
                        total_char_num += 1

            if sub_overlap:
                if len(sub_group_idx_list) == 0:
                    sub_group_idx_list.append(i)
                else:
                    hor_diff = hss_group.me_groups[i].left() - sub_right_bound
                    if hor_diff < 2.0 * total_char_width/total_char_num:
                        sub_group_idx_list.append(i)
                        sub_right_bound = hss_group.me_groups[i].right()
                        total_char_width += hss_group.me_groups[i].width()
                        total_char_num += 1

            i += 1
            # end of the while loop to extend

        # create new groups here
        sup_me_groups = [hss_group.me_groups[i] for i in sup_group_idx_list]
        sub_me_groups = [hss_group.me_groups[i] for i in sub_group_idx_list]
        sup_hss_group = MEHSSGroup(sup_me_groups)
        sub_hss_group = MEHSSGroup(sub_me_groups)
        # recursively organize the sup and sub part
        sup_hs_group = organize_subandsup_in_hss(sup_hss_group)
        sub_hs_group = organize_subandsup_in_hss(sub_hss_group)

        left_me_groups = []
        for i, me_group in enumerate(hss_group.me_groups):
            if i in sup_group_idx_list or \
                    i in sub_group_idx_list or\
                    i == sup_sub_base_idx:
                continue
            left_me_groups.append(me_group)
        new_sup_sub_group = MESupSubGroup(
            hss_group.me_groups[sup_sub_base_idx],
            sup_hs_group,
            sub_hs_group)
        left_me_groups.append(new_sup_sub_group)
        hss_group.me_groups = left_me_groups

    hss_group.me_groups.sort(key=lambda mg:mg.left())
    hs_group = MEHorSupOrSubGroup(hss_group.me_groups)
    return hs_group
