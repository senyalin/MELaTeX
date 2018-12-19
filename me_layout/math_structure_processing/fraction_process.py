"""
It is a bottom up approach, thus no recursion here.

The way it's done: find the minimal fraction line.

Find the char above it, THIS MIGHT NOT BE A GOOD CHOICE.

The current way of grouping might not be correct for special cases.
TWO FRACTION LINE of the same length and same horizontal location.

Given a fraction line,
* first find char within the horizontal range
* split the char into above and lower
* then use horizontal PPC to split the chars
** and then find the lowest for the char above the fraction line, add to upper set
** find the highest for chars under the fraction line, add to lower set
* then iteratively add more chars to the upper/lower set
    if the char overlap vertically with the range of current set

"""

from pdfxml.me_layout.me_group.vertical_me_group import MEFractionGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath
from pdfxml.me_layout.math_structure_processing.ppc_expand import iterative_expanding_idx
from pdfxml.me_layout.pss_exp.pss_exception import ComponentEmptyException


def organize_fraction_in_ugp(ugp):
    while True:
        smallest_fraction_path = get_smallest_fraction_path(ugp)
        if smallest_fraction_path == None:
            break # no more to do

        #  fraction_path_bbox = smallest_fraction_path.get_tight_bbox()
        # later
        """
        
        fraction_up_me_groups = iterative_expanding(
            ugp,
            #smallest_fraction_path.tight_top(),
            smallest_fraction_path.tight_bottom(),
            "up",
            (smallest_fraction_path.left(), smallest_fraction_path.right()),
            options="half_hor"
        )
        fraction_down_me_groups = iterative_expanding(
            ugp,
            # smallest_fraction_path.tight_bottom(),
            smallest_fraction_path.tight_top(), # when doing the down part, use the top boundary
            "down",
            (smallest_fraction_path.left(), smallest_fraction_path.right()),
            options="half_hor"
        )
        """
        fraction_up_me_groups_idx = iterative_expanding_idx(
            ugp,
            # smallest_fraction_path.tight_top(),
            smallest_fraction_path.tight_bottom(),
            "up",
            (smallest_fraction_path.left(), smallest_fraction_path.right()),
            options="half_hor"
        )
        fraction_down_me_groups_idx = iterative_expanding_idx(
            ugp,
            # smallest_fraction_path.tight_bottom(),
            smallest_fraction_path.tight_top(), # when doing the down part, use the top boundary
            "down",
            (smallest_fraction_path.left(), smallest_fraction_path.right()),
            options="half_hor"
        )

        # NOTE, TODO, the effect is to be tested
        # how about still make it unorganized here, otherwise, some logic will not be triggerred
        # but not sure how to logic will change for other
        # though they tend to be HSS, but I still need to treat them as UGP to trigger some logic

        if len(fraction_up_me_groups_idx) == 0 and len(fraction_down_me_groups_idx) != 0:
            # create an accent group here.

            raise Exception("TODO, create an accent structure overline bar")
            pass

        if len(fraction_up_me_groups_idx) == 0 or len(fraction_down_me_groups_idx) == 0:
            raise ComponentEmptyException()

        fraction_up_me_groups = [ugp.me_groups[idx] for idx in fraction_up_me_groups_idx]
        fraction_down_me_groups = [ugp.me_groups[idx] for idx in fraction_down_me_groups_idx]
        up_hss_group = UnorganizedGroupPath(fraction_up_me_groups, [])
        down_hss_group = UnorganizedGroupPath(fraction_down_me_groups, [])
        me_fraction_group = MEFractionGroup(
            smallest_fraction_path,
            up_hss_group,
            down_hss_group)

        keep_me_groups = []
        for i, me_group in enumerate(ugp.me_groups):
            # also the matching is not object matching, but value mathcing here.
            if i in fraction_up_me_groups_idx or i in fraction_down_me_groups_idx:
                continue
            keep_me_groups.append(ugp.me_groups[i])
        keep_me_paths = [me_path for me_path in ugp.me_paths if me_path != smallest_fraction_path]
        keep_me_groups.append(me_fraction_group)
        keep_me_groups.sort(key=lambda mg:mg.left())
        ugp.set_me_groups(keep_me_groups)
        ugp.set_me_paths(keep_me_paths)


def get_smallest_fraction_path(ugp):
    """
    if no other path, horizontally within the target path

    :param ugp: assuming all the me_paths for now are only fractions
    :return:
    """
    for i, me_path in enumerate(ugp.me_paths):
        no_other_within = True
        for j in range(len(ugp.me_paths)):
            if i == j:
                continue
            if ugp.me_paths[j].get_tight_bbox().left() > me_path.get_tight_bbox().left() and\
                    ugp.me_paths[j].get_tight_bbox().right() < me_path.get_tight_bbox().right():
                no_other_within = False
                break
        if no_other_within:
            return me_path
    return None


if __name__ == '__main__':
    #test_fraction()
    pass
