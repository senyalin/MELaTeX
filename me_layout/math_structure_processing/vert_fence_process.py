from pdfxml.me_layout.math_structure_processing.common_process import seperate_me_group
from pdfxml.me_layout.me_group.atomic_me_group import MESymbolGroup
from pdfxml.me_layout.me_group.enclosed_me_group import MEFenceGroup
from pdfxml.me_layout.me_group.internal_me_group import MEHorSupOrSubGroup
from pdfxml.me_layout.me_group.hor_me_group import MESubGroup, MESupGroup, MEHorGroup
from pdfxml.me_layout.me_group.vertical_me_group import MESupSubGroup, MEFractionGroup
from pdfxml.me_layout.pss_exp.pss_exception import ComponentEmptyException


def vert_only_two(hs_group, i, j):
    """

    :param hs_group:
    :param i:
    :param j:
    :return:
    """

    if isinstance(hs_group, MEHorGroup) and len(hs_group.me_groups) == 2 and \
            str(hs_group.me_groups[0]) == '|' and str(hs_group.me_groups[0]).startswith('|'):
        return hs_group
    # simple case
    # use the first and the last to seperate the groups
    in_fence_me_groups, out_fence_me_groups = seperate_me_group(hs_group.me_groups, i, j)

    # no more component empty exception
    #if len(in_fence_me_groups) == 0:
    #raise ComponentEmptyException()


    if len(in_fence_me_groups) == 0:
        return hs_group
        #ttt = 1
    in_hs_group = MEHorSupOrSubGroup(in_fence_me_groups)

    if not isinstance(hs_group.me_groups[i], MESymbolGroup):
        return hs_group  # do not merge, resolve later.

    if isinstance(hs_group.me_groups[j], MESupSubGroup) or isinstance(hs_group.me_groups[j], MESupGroup) or \
            isinstance(hs_group.me_groups[j], MESubGroup):

        # create a fence group update the based of the MESubSubGroup
        me_fence_group = MEFenceGroup(
            in_hs_group,
            hs_group.me_groups[i].me_symbol,
            hs_group.me_groups[j].base_me_group.me_symbol
        )
        tmp_group = hs_group.me_groups[j]
        tmp_group.base_me_group = me_fence_group
        me_fence_group = tmp_group # reassign by the end
        # TODO, confirm whether applicable to the sup or sub

    elif isinstance(hs_group.me_groups[j], MESymbolGroup):
        me_fence_group = MEFenceGroup(
            in_hs_group,
            hs_group.me_groups[i].me_symbol,
            hs_group.me_groups[j].me_symbol
        )
    else:
        raise Exception("Unknown type")

    out_fence_me_groups.append(me_fence_group)
    out_fence_me_groups.sort(key=lambda me_group: me_group.left())
    hs_group.me_groups = out_fence_me_groups
    return hs_group


def double_vert_four(hs_group, i, j, k, l):
    """
    there are two double vertical bar, need to create HOR group for them with MEHorSupOrSubGroup

    :param hs_group:
    :param i:
    :param j:
    :param k:
    :param l:
    :return:
    """
    # create one group, but not as fence due to how the fence structure is defined.
    in_fence_me_groups, out_fence_me_groups = seperate_me_group(
        hs_group.me_groups, j, k, [i, l]
    )

    # since the FenceGroup need the MESymbol, use the MEHorGroup structure instead

    hg1 = MEHorGroup([hs_group.me_groups[i], hs_group.me_groups[j]])
    if len(in_fence_me_groups) == 0:
        raise ComponentEmptyException()
    hssg = MEHorSupOrSubGroup(in_fence_me_groups)
    hg2 = MEHorGroup([hs_group.me_groups[k], hs_group.me_groups[l]])

    hg = MEHorGroup([hg1, hssg, hg2])

    out_fence_me_groups.append(hg)
    out_fence_me_groups.sort(key=lambda me_group: me_group.left())
    hs_group.me_groups = out_fence_me_groups
    return hs_group


def two_vert_pairs(hs_group, i, j, k, l):
    """
    There are two pairs of vertical fence

    :param hs_group:
    :param i:
    :param j:
    :param k:
    :param l:
    :return:
    """
    hs_group = vert_only_two(hs_group, i, j)
    # after the first processing, the index is shifted
    hs_group = organize_vert_in_hs_group(hs_group)
    #hs_group = vert_only_two(hs_group, k, l)
    return hs_group


def get_double_vert_pair(idx_list):
    """

    :param idx_list:
    :return: None if not found
    """
    idx_list.sort() # from small to large
    # find all consecutive pairs
    start_idx_list = []
    for i, idx in enumerate(idx_list):
        if i+1 < len(idx_list) and idx_list[i]+1 == idx_list[i+1]:
            start_idx_list.append(i)
    if len(start_idx_list) >= 2:
        # equality condition
        # NOTE, for the double vertical bar, make assumption that no nested.
        return [
            idx_list[start_idx_list[0]],
            idx_list[start_idx_list[0]] + 1,
            idx_list[start_idx_list[1]],
            idx_list[start_idx_list[1]] + 1,
        ]
    return None


def is_free_vert_bar(me_group):
    """
    check whether an me_group is to be matched

    :param me_group:
    :return:
    """
    mg_str = str(me_group)
    if isinstance(me_group, MEFenceGroup):
        return False
    if isinstance(me_group, MEFractionGroup):
        return False
    if isinstance(me_group, MEHorGroup):
        if len(me_group.me_groups) == 3:
            # clean double vert fence
            if mg_str.startswith("||") and mg_str.endswith("||"):
                return False

            # vert fence with script
            sub_mg_str1 = str(me_group.me_groups[0])
            sub_mg_str3 = str(me_group.me_groups[2])
            if sub_mg_str1.startswith("||") and sub_mg_str3.startswith("||"):
                return False

            # if have three elements, little chance to be a free |
            return False

        # TODO, other wise, not well defined?
        if len(me_group.me_groups) == 2 and str(me_group) == '||':
            # already created double fence
            return False

        return mg_str.startswith("|")
        #raise Exception("TODO not well defined")
    return mg_str.startswith("|")


def organize_vert_in_hs_group(hs_group):
    """
    This module is called after the asymmetric pair is done.
    First count how many vert there are


    :param hs_group:
    :return:
    """

    # TODO, !!!
    # the element between the fence should not have total height larger than the fence.
    # otherwise, will not group them.

    vert_bar_indice = []
    for i, me_group in enumerate(hs_group.me_groups):
        # as long as starting with the | symbol,
        #if not isinstance(me_group, MESymbolGroup):
        #    continue
        if is_free_vert_bar(me_group):
            vert_bar_indice.append(i)

    if len(vert_bar_indice) % 2 != 0:
        # odd number, could not match the pairs
        return hs_group

    if len(vert_bar_indice) == 0:
        return hs_group
    if len(vert_bar_indice) == 2:
        return vert_only_two(hs_group, vert_bar_indice[0], vert_bar_indice[1])
    elif len(vert_bar_indice) == 4:
        # check for double vert bar
        # double bar case
        if vert_bar_indice[0]+1 == vert_bar_indice[1] and \
                vert_bar_indice[2] + 1 == vert_bar_indice[3] and \
                vert_bar_indice[1]+1 != vert_bar_indice[3]:
            hs_group = double_vert_four(
                hs_group, vert_bar_indice[0], vert_bar_indice[1], vert_bar_indice[2], vert_bar_indice[3]
            )
            return hs_group

        elif vert_bar_indice[0]+1 < vert_bar_indice[1] and \
                vert_bar_indice[2] + 1 < vert_bar_indice[3]:
            # create two group
            return two_vert_pairs(
                hs_group,
                vert_bar_indice[0], vert_bar_indice[1], vert_bar_indice[2], vert_bar_indice[3]
            )
        else:
            raise Exception("Unknown 4 vertical bars arrangement")
    elif len(vert_bar_indice) == 6:
        double_vert_quadruple = get_double_vert_pair(vert_bar_indice)
        if double_vert_quadruple is not None:
            # could find matched pairs
            hs_group = double_vert_four(
                hs_group, double_vert_quadruple[0], double_vert_quadruple[1], double_vert_quadruple[2], double_vert_quadruple[3]
            )
            return organize_vert_in_hs_group(hs_group)
        else:
            # make assumption that no nested, then greedy choose the cases
            # first group the first item, then recursively call the function to work on the left
            hs_group = vert_only_two(hs_group, vert_bar_indice[0], vert_bar_indice[1])
            return organize_vert_in_hs_group(hs_group)
    elif len(vert_bar_indice) == 8:
        double_vert_quadruple = get_double_vert_pair(vert_bar_indice)
        if double_vert_quadruple is not None:
            hs_group = double_vert_four(
                hs_group, double_vert_quadruple[0], double_vert_quadruple[1], double_vert_quadruple[2],
                double_vert_quadruple[3]
            )
            return organize_vert_in_hs_group(hs_group)
        else:
            hs_group = vert_only_two(hs_group, vert_bar_indice[0], vert_bar_indice[1])
            return organize_vert_in_hs_group(hs_group)
    else:
        double_vert_quadruple = get_double_vert_pair(vert_bar_indice)
        if double_vert_quadruple is not None:
            # could find matched pairs
            hs_group = double_vert_four(
                hs_group, double_vert_quadruple[0], double_vert_quadruple[1], double_vert_quadruple[2],
                double_vert_quadruple[3]
            )
            return organize_vert_in_hs_group(hs_group)
        else:
            # make assumption that no nested, then greedy choose the cases
            # first group the first item, then recursively call the function to work on the left
            hs_group = vert_only_two(hs_group, vert_bar_indice[0], vert_bar_indice[1])
            return organize_vert_in_hs_group(hs_group)
        # not sure about the situation.
        #raise Exception("Unknown {} vertical bars arrangement".format(len(vert_bar_indice)))
    #return hs_group