"""
hat processing means from UGP, find the hat symbol and all the symbols covered under it.
"""
import copy

from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.vertical_me_group import MEAccentGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath
from pdfxml.me_layout.math_structure_processing.ppc_expand import iterative_expanding_idx
from pdfxml.me_taxonomy.math_resources import accent_name_list, under_name_list

over_char_list = ["\\"+hat_name for hat_name in accent_name_list]
under_char_list = ["\\"+under_name for under_name in under_name_list]
hat_char_list = copy.copy(over_char_list)
hat_char_list.extend(under_char_list)


def organize_hat_in_ugp(ugp):
    """
    Through this example 28012673, find a bug that the underline just touch the boundary of the italic X
    causing the X as the above part of the underline structure

    find the hat chars
    :param ugp:
    :type ugp: UnorganizedGroupPath
    :return:
    """
    while True:
        # sort the hat symbol by the bottom
        hat_symbol_groups_idx = []
        for i, me_group in enumerate(ugp.me_groups):
            if isinstance(me_group, MESymbolGroup):
                if str(me_group) in hat_char_list:
                    hat_symbol_groups_idx.append(i)
        if len(hat_symbol_groups_idx) == 0:
            break
        hat_symbol_groups_idx.sort(key=lambda idx:ugp.me_groups[idx].tight_top())
        hat_symbol_groups = [ugp.me_groups[i] for i in hat_symbol_groups_idx]

        # call extend
        hat_symbol_group_idx = hat_symbol_groups_idx[0]
        hat_symbol_group = hat_symbol_groups[0]
        if str(hat_symbol_group) in over_char_list:
            new_me_groups_idx = iterative_expanding_idx(
                ugp,
                hat_symbol_group.tight_bottom(),
                "down",
                (hat_symbol_group.left(), hat_symbol_group.right()),
                options="half_hor"
            )
            new_me_groups = [ugp.me_groups[i] for i in new_me_groups_idx]
        elif str(hat_symbol_group) in under_char_list:
            new_me_groups_idx = iterative_expanding_idx(
                ugp,
                hat_symbol_group.tight_top(),
                "up",
                (hat_symbol_group.left(), hat_symbol_group.right()),
                options="half_hor"
            )
            new_me_groups = [ugp.me_groups[i] for i in new_me_groups_idx]
        else:
            raise Exception("logical error, should not be here")

        if len(new_me_groups) == 0:
            #raise ComponentEmptyException()
            pass

        if len(new_me_groups) == 0:
            new_ugp = EmptyGroup()
        else:
            new_ugp = UnorganizedGroupPath(new_me_groups, [])

        new_hat_group = MEAccentGroup(hat_symbol_group.me_symbol, new_ugp)
        keep_me_groups = []
        for i, me_group in enumerate(ugp.me_groups):
            if i in new_me_groups_idx:
                continue
            if i == hat_symbol_group_idx:
                continue
            keep_me_groups.append(me_group)
        keep_me_groups.append(new_hat_group)
        ugp.set_me_groups(keep_me_groups)
