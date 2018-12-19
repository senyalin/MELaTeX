"""
bind var operation indicates:
    sum, prod, and some others

NOTE:
    there are still many experimental ideas tried here.
    some case to handle:
        * expand beyond the limit of the bind operator, try to write another version of PPC expansion in the ppc_expand.py file
        * when there is consecutive of two Big operator, split by the middle.
"""
from pdfxml.pdf_util.layout_util import merge_bbox_list
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.vertical_me_group import MEBindVarGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath
from pdfxml.me_layout.math_structure_processing.ppc_expand import iterative_expanding_v2_idx
from pdfxml.me_taxonomy.math_resources import big_op_name_list


big_op_latex_val_list = ["\\"+char_name for char_name in big_op_name_list]


def is_big_op_me_symbol_group(mg):
    if isinstance(mg, MESymbolGroup):
        if mg.me_symbol.latex_val in big_op_latex_val_list:
            return True
    return False


def find_consecutive_bind_op_idx_list(ugp):
    """
    find consecutive binding operators
    not other overlapping vertically between them

    :param ugp:
    :return:
    """
    big_op_mg_idx_list = []
    ugp.me_groups.sort(key=lambda mg: mg.get_tight_bbox().left())
    for i, mg in enumerate(ugp.me_groups):
        if is_big_op_me_symbol_group(mg):
            big_op_mg_idx_list.append(i)

    is_consecutive_list = [True]* (len(big_op_mg_idx_list)-1)
    for i in range(len(big_op_mg_idx_list)-1):

        first_big_op_idx = big_op_mg_idx_list[i]
        second_big_op_idx = big_op_mg_idx_list[i+1]
        first_big_op = ugp.me_groups[first_big_op_idx]
        second_big_op = ugp.me_groups[second_big_op_idx]
        first_big_op_bbox = first_big_op.get_tight_bbox()
        second_big_op_bbox = second_big_op.get_tight_bbox()

        if not first_big_op_bbox.v_overlap(second_big_op_bbox):
            is_consecutive_list[i] = False
            continue

        for j in range(first_big_op_idx+1, second_big_op_idx):
            if first_big_op_bbox.v_overlap(ugp.me_groups[j].get_tight_bbox()):
                is_consecutive_list[i] = False
                break
            if second_big_op_bbox.v_overlap(ugp.me_groups[j].get_tight_bbox()):
                is_consecutive_list[i] = False
                break

    i = 0
    while i < len(big_op_mg_idx_list)-1:
        if is_consecutive_list[i]:  # i is the start index
            j = i
            while j < len(big_op_mg_idx_list)-1 and is_consecutive_list[j]:
                j += 1
            # include j
            return big_op_mg_idx_list[i:j+1]
        else:
            i += 1
    return None


def create_consecutive_bind_var_list(ugp, consecutive_bind_op_idx_list, up_me_groups_idx, down_me_groups_idx):
    """
    # split the upper and lower for each of them.
    # process one by one
    # first for the item with left boundary less than the right boundary of the current big op
    # then for between the two, find the two with the largest gap,
    # previous belong to the previous


    :param ugp:
    :param consecutive_bind_op_idx_list:
    :param up_me_groups_idx:
    :param down_me_groups_idx:
    :return:
    """
    upper_cur_idx = 0  # current to concern
    under_cur_idx = 0
    cur_big_op_i = 0

    # TODO
    upper_mg_idx_list_list = []  # upper part
    under_mg_idx_list_list = []  # under part

    while cur_big_op_i < len(consecutive_bind_op_idx_list):
        cur_big_op_idx = consecutive_bind_op_idx_list[cur_big_op_i]

        tmp_upper_mg_idx_list = []
        tmp_under_mg_idx_list = []
        # upper part
        while upper_cur_idx < len(up_me_groups_idx) and \
                ugp.me_groups[up_me_groups_idx[upper_cur_idx]].get_tight_bbox().left() < ugp.me_groups[
            cur_big_op_idx].get_tight_bbox().right():
            tmp_upper_mg_idx_list.append(up_me_groups_idx[upper_cur_idx])
            upper_cur_idx += 1

        # under part
        while under_cur_idx < len(down_me_groups_idx) and \
                ugp.me_groups[down_me_groups_idx[under_cur_idx]].get_tight_bbox().left() < ugp.me_groups[
            cur_big_op_idx].get_tight_bbox().right():
            tmp_under_mg_idx_list.append(down_me_groups_idx[under_cur_idx])
            under_cur_idx += 1

        # decide the boundary to go beyong
        # find the next until the right larger than the left boundary
        if cur_big_op_i + 1 < len(consecutive_bind_op_idx_list):
            next_big_op_idx = consecutive_bind_op_idx_list[cur_big_op_i + 1]
            upper_next_idx = upper_cur_idx
            under_next_idx = under_cur_idx
            while upper_next_idx < len(up_me_groups_idx) and \
                    ugp.me_groups[up_me_groups_idx[upper_next_idx]].get_tight_bbox().right() < ugp.me_groups[
                next_big_op_idx].get_tight_bbox().left():
                upper_next_idx += 1
            while under_next_idx < len(down_me_groups_idx) and \
                    ugp.me_groups[down_me_groups_idx[under_next_idx]].get_tight_bbox().right() < ugp.me_groups[
                next_big_op_idx].get_tight_bbox().left():
                under_next_idx += 1

            # find the split point
            # between the upper_cur_idx and the upper_next_idx
            upper_last_idx = upper_cur_idx - 1
            if upper_last_idx >= 0:
                upper_largest_gap = ugp.me_groups[up_me_groups_idx[upper_last_idx + 1]].get_tight_bbox().left() - \
                                    ugp.me_groups[up_me_groups_idx[upper_last_idx]].get_tight_bbox().right()
                tmpi = upper_last_idx
                while tmpi < upper_next_idx:
                    tmp_gap = ugp.me_groups[up_me_groups_idx[tmpi + 1]].get_tight_bbox().left() - \
                              ugp.me_groups[up_me_groups_idx[tmpi]].get_tight_bbox().right()
                    if tmp_gap > upper_largest_gap:
                        upper_last_idx = tmpi
                    tmpi += 1

                while upper_cur_idx <= upper_last_idx:
                    tmp_upper_mg_idx_list.append(up_me_groups_idx[upper_cur_idx])
                    upper_cur_idx += 1

            # between the under_cur_idx and the under_next_idx
            under_last_idx = under_cur_idx - 1
            if under_last_idx >= 0 and under_last_idx + 1 < len(down_me_groups_idx):
                under_largest_gap = ugp.me_groups[down_me_groups_idx[under_last_idx + 1]].get_tight_bbox().left() - \
                                    ugp.me_groups[down_me_groups_idx[under_last_idx]].get_tight_bbox().right()
                tmpi = under_last_idx
                while tmpi < under_next_idx and tmpi+1 < len(down_me_groups_idx):
                    tmp_gap = ugp.me_groups[down_me_groups_idx[tmpi + 1]].get_tight_bbox().left() - \
                              ugp.me_groups[down_me_groups_idx[tmpi]].get_tight_bbox().right()
                    if tmp_gap > under_largest_gap:
                        under_last_idx = tmpi
                    tmpi += 1

                while under_cur_idx <= under_last_idx:
                    tmp_under_mg_idx_list.append(down_me_groups_idx[under_cur_idx])
                    under_cur_idx += 1

            upper_mg_idx_list_list.append(tmp_upper_mg_idx_list)
            under_mg_idx_list_list.append(tmp_under_mg_idx_list)
        else:
            while under_cur_idx < len(down_me_groups_idx):
                tmp_under_mg_idx_list.append(down_me_groups_idx[under_cur_idx])
                under_cur_idx += 1
            while upper_cur_idx < len(up_me_groups_idx):
                tmp_upper_mg_idx_list.append(up_me_groups_idx[upper_cur_idx])
                upper_cur_idx += 1
            upper_mg_idx_list_list.append(tmp_upper_mg_idx_list)
            under_mg_idx_list_list.append(tmp_under_mg_idx_list)
        cur_big_op_i += 1

    bind_var_list = []
    for i, bind_op_idx in enumerate(consecutive_bind_op_idx_list):
        bind_var_symbol = ugp.me_groups[bind_op_idx]
        if len(upper_mg_idx_list_list[i]) == 0:
            tmp_upper_me_group = EmptyGroup()
        else:
            tmp_upper_me_group = UnorganizedGroupPath([ugp.me_groups[j] for j in upper_mg_idx_list_list[i]], [])
        if len(under_mg_idx_list_list[i]) == 0:
            tmp_under_me_group = EmptyGroup()
        else:
            tmp_under_me_group = UnorganizedGroupPath([ugp.me_groups[j] for j in under_mg_idx_list_list[i]], [])
        bind_var_group = MEBindVarGroup(bind_var_symbol, tmp_upper_me_group, tmp_under_me_group)
        bind_var_list.append(bind_var_group)
    return bind_var_list


def organize_consecutive_bind_var_in_ugp(ugp):
    """
    Assumption that the upper/under of one will not fall under others.
    Use the gap between them to find the related charactes.

    Use all the op toghether to expand the upper and under.

    :param ugp:
    :return:
    """
    while True:
        consecutive_bind_op_idx_list = find_consecutive_bind_op_idx_list(ugp)
        if consecutive_bind_op_idx_list is None:
            break

        big_op_bbox = merge_bbox_list([ugp.me_groups[i].get_tight_bbox() for i in consecutive_bind_op_idx_list])
        # expand on the upper and lower
        up_me_groups_idx = iterative_expanding_v2_idx(
            ugp, big_op_bbox.top(), "up", (big_op_bbox.left(), big_op_bbox.right()))
        up_me_groups_idx.sort(key=lambda idx:ugp.me_groups[idx].left())
        #up_me_groups = [ugp.me_groups[i] for i in up_me_groups_idx]
        #up_me_groups.sort(key=lambda mg: mg.left())

        # down_me_groups = iterative_expanding(
        down_me_groups_idx = iterative_expanding_v2_idx(
            ugp, big_op_bbox.bottom(), "down", (big_op_bbox.left(), big_op_bbox.right()))
        down_me_groups_idx.sort(key=lambda idx:ugp.me_groups[idx].left())
        #down_me_groups = [ugp.me_groups[i] for i in down_me_groups_idx]
        #down_me_groups.sort(key=lambda mg: mg.left())

        bind_var_list = create_consecutive_bind_var_list(ugp, consecutive_bind_op_idx_list, up_me_groups_idx, down_me_groups_idx)

        left_me_groups = []
        for i, me_group in enumerate(ugp.me_groups):
            if i in consecutive_bind_op_idx_list or \
                    i in up_me_groups_idx or \
                    i in down_me_groups_idx:
                continue
            left_me_groups.append(me_group)
        left_me_groups.extend(bind_var_list)
        left_me_groups.sort(key=lambda mg: mg.left())
        ugp.set_me_groups(left_me_groups)

    return ugp


def organize_bind_var_in_ugp(ugp):
    """
    BUG: equal lost, also becuase of the element matching issues

    check each character by the latex name,

    create a list of op that might associate the binding variable

    for the upper and lower part, UGP group for them

    should use the procedure in the hat / fraction processing
    that keep expanding

    :param ugp:
    :type ugp: UnorganizedGroupPath
    :return:
    :rtype: UnorganizedGroupPath
    """

    ugp = organize_consecutive_bind_var_in_ugp(ugp)  # processing of the consecutive

    while True:
        big_op_symbol_group_idx = None
        big_op_symbol_group = None
        for i, me_group in enumerate(ugp.me_groups):
            if is_big_op_me_symbol_group(me_group):
                big_op_symbol_group_idx = i
                big_op_symbol_group = me_group
                break

        if big_op_symbol_group_idx is None:
            break

        # TODO, find the consecutive binding variable symbols

        # TODO, NOTE, supposing no path in the over or under for now
        # vpos, direction, hrange)
        #iterative_expanding_v2
        #up_me_groups = iterative_expanding(
        up_me_groups_idx = iterative_expanding_v2_idx(
            ugp, big_op_symbol_group.get_tight_bbox().top(), "up",
            (
                big_op_symbol_group.get_tight_bbox().left(),
                big_op_symbol_group.get_tight_bbox().right()
            )
        )
        up_me_groups = [ugp.me_groups[i] for i in up_me_groups_idx]
        up_me_groups.sort(key=lambda mg: mg.left())

        #down_me_groups = iterative_expanding(
        down_me_groups_idx = iterative_expanding_v2_idx(
            ugp, big_op_symbol_group.get_tight_bbox().bottom(), "down",
            (
                big_op_symbol_group.get_tight_bbox().left(),
                big_op_symbol_group.get_tight_bbox().right()
            ))
        down_me_groups = [ugp.me_groups[i] for i in down_me_groups_idx]
        down_me_groups.sort(key=lambda mg: mg.left())

        # even if both empty, still do this, only to make it iteration good.
        # by changing from SYMBOL to BINDVAR, mark as processed.
        up_ugp_group = UnorganizedGroupPath(up_me_groups, []) if up_me_groups else EmptyGroup()
        down_ugp_group = UnorganizedGroupPath(down_me_groups, []) if down_me_groups else EmptyGroup()

        bind_var_group = MEBindVarGroup(big_op_symbol_group, up_ugp_group, down_ugp_group)
        left_me_groups = []
        for i, me_group in enumerate(ugp.me_groups):
            if i == big_op_symbol_group_idx or \
                    i in up_me_groups_idx or \
                    i in down_me_groups_idx:
                continue
            left_me_groups.append(me_group)

        left_me_groups.append(bind_var_group)
        left_me_groups.sort(key=lambda mg: mg.left())
        ugp.set_me_groups(left_me_groups)

