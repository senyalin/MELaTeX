"""
projection profiling cuting based expanding of the MEGroup
"""
import numpy as np
from pdfxml.me_layout.me_group.atomic_me_group import MESymbolGroup
from pdfxml.pdf_util.bbox import bbox_h_overlapping, BBox, bbox_v_overlapping, merge_bbox


def iterative_expanding_idx(ugp, vpos, direction, hrange, options='default'):
    """
    This is a general function that is in charging of many structures,
    such as the fraction line, the radical part analysis.

    :param options:
        "default", just as the original version,
        "half_hor", at least with half of the horizontal range overlapping

    :param ugp: UnorganizedGroupPath, only the me_paths to consider here
    :param vpos: vertical position of concern
    :param direction: "up" or "down"

    :param hrange:
        tuple of two

    :return: list of index for the MEGroup
    :rtype: list[int]
    """
    # TODO, also consider the me_path, and give expection when matched.
    tmp_bbox = BBox([hrange[0], vpos, hrange[1], vpos])

    # first gather the candiates by the horizontal groups
    cand_me_groups_idx = []
    for i, me_group in enumerate(ugp.me_groups):
        if bbox_h_overlapping(me_group.get_tight_bbox(), tmp_bbox):
            if direction == "up" and me_group.get_tight_bbox().bottom() >= vpos:
                cand_me_groups_idx.append(i)
            if direction == "down" and me_group.get_tight_bbox().top() <= vpos:
                cand_me_groups_idx.append(i)

    # create the seed here
    if direction == "up":
        cand_me_groups_idx.sort(key=lambda idx: ugp.me_groups[idx].get_tight_bbox().bottom())
    if direction == "down":
        cand_me_groups_idx.sort(key=lambda idx: -1*ugp.me_groups[idx].get_tight_bbox().top())

    if len(cand_me_groups_idx) > 0:
        tmp_bbox.set_bottom(ugp.me_groups[cand_me_groups_idx[0]].get_tight_bbox().bottom())
        tmp_bbox.set_top(ugp.me_groups[cand_me_groups_idx[0]].get_tight_bbox().top())

        confirmed_me_groups_idx = [cand_me_groups_idx[0]]
        while True:
            new_adding = False
            for cand_me_group_idx in cand_me_groups_idx:
                if cand_me_group_idx in confirmed_me_groups_idx:
                    continue
                cur_cand_me_group = ugp.me_groups[cand_me_group_idx]

                from pdfxml.me_layout.char_adjust_bbox_core import could_estimate_height
                if isinstance(cur_cand_me_group, MESymbolGroup) and could_estimate_height(cur_cand_me_group):
                    v_overlap = bbox_v_overlapping(tmp_bbox, cur_cand_me_group.get_adjusted_bbox())
                else:
                    v_overlap = bbox_v_overlapping(tmp_bbox, cur_cand_me_group.get_tight_bbox())

                """
                me_parsing_logger.debug("check overlapping {} and {} as {}".format(
                    tmp_bbox,
                    ugp.me_groups[cand_me_group_idx].get_tight_bbox(),
                    v_overlap
                ))
                """
                if v_overlap:
                    # The vertical overlapping is the first condition that must be sat in call cases
                    if options == 'default':
                        confirmed_me_groups_idx.append(cand_me_group_idx)
                        new_adding = True
                        tmp_bbox = merge_bbox(tmp_bbox, ugp.me_groups[cand_me_group_idx].get_tight_bbox())
                    elif options == 'half_hor':
                        # in the horizontal direction, at least overlapping half of the horizontal range
                        tight_bbox = ugp.me_groups[cand_me_group_idx].get_tight_bbox()

                        max_left = max(tight_bbox.left(), hrange[0])
                        min_right = min(tight_bbox.right(), hrange[1])
                        if min_right >= max_left:
                            tmp_len = min_right - max_left
                            if tmp_len > (tight_bbox.right()-tight_bbox.left())/2:
                                confirmed_me_groups_idx.append(cand_me_group_idx)
                                new_adding = True
                                tmp_bbox = merge_bbox(tmp_bbox, ugp.me_groups[cand_me_group_idx].get_tight_bbox())
                    else:
                        raise Exception("unknown options: {}".format(options))

            if new_adding == False:
                break
        return confirmed_me_groups_idx
    else:
        return []


def iterative_expanding_v2_idx(ugp, vpos, direction, hrange):
    """
    only return the index, not the me obj, as I don't have reference level comparison

    only design for the bind var under and over
     assume mostly in a line

    one problem in the first version is that it hard limit the bound,

    first only get the element under or over

    :return:
    """
    cand_me_groups_idx = []
    for i, me_group in enumerate(ugp.me_groups):
        if direction == "up" and me_group.get_tight_bbox().bottom() >= vpos:
            #cand_me_groups.append(me_group)
            cand_me_groups_idx.append(i)
        if direction == "down" and me_group.get_tight_bbox().top() <= vpos:
            #cand_me_groups.append(me_group)
            cand_me_groups_idx.append(i)

    if len(cand_me_groups_idx) == 0:
        return []

    cand_me_groups_idx.sort(
        key=lambda idx: ugp.me_groups[idx].get_center()[0])
    bind_var_hor_center = (hrange[0]+hrange[1])/2.0
    mid_idx = 0
    for i in range(len(cand_me_groups_idx)):
        mid_mg = ugp.me_groups[cand_me_groups_idx[mid_idx]]
        mg = ugp.me_groups[cand_me_groups_idx[i]]

        min_dist = np.abs(mid_mg.get_center()[0]-bind_var_hor_center)
        cur_dist = np.abs(mg.get_center()[0]-bind_var_hor_center)
        if cur_dist < min_dist:
            mid_idx = i

    # if the middle one is even not in the scope, just return []
    mid_hor = ugp.me_groups[cand_me_groups_idx[mid_idx]].get_center()[0]
    if not (hrange[0] <= mid_hor <= hrange[1]):
        return []

    # TODO, confirm with the deprecated function
    avg_size = np.mean([ugp.me_groups[idx].width() for idx in cand_me_groups_idx])

    from pdfxml.me_layout.me_layout_config import horizontal_consecutive_width_ratio
    #expanding from the middle
    left_idx = mid_idx
    while left_idx > 0:
        dist = \
            ugp.me_groups[cand_me_groups_idx[left_idx]].left() - \
            ugp.me_groups[cand_me_groups_idx[left_idx-1]].right()
        next_in_range = hrange[0] <= ugp.me_groups[cand_me_groups_idx[left_idx-1]].get_center()[0] <= hrange[1]

        should_add_next = next_in_range or dist < horizontal_consecutive_width_ratio*avg_size
        if should_add_next:
            left_idx -= 1

        if dist < horizontal_consecutive_width_ratio*avg_size:
            pass
        else:
            break

    right_idx = mid_idx
    while right_idx < len(cand_me_groups_idx)-1:
        dist = \
            ugp.me_groups[cand_me_groups_idx[right_idx+1]].left()- \
            ugp.me_groups[cand_me_groups_idx[right_idx]].right()
        next_in_range = hrange[0] <= ugp.me_groups[cand_me_groups_idx[right_idx+1]].get_center()[0] <= hrange[1]
        should_add = next_in_range or dist < horizontal_consecutive_width_ratio * avg_size
        if should_add:
            right_idx += 1

        if dist < horizontal_consecutive_width_ratio*avg_size:
            pass
        else:
            break
    # only return the index position
    return [cand_me_groups_idx[i] for i in range(left_idx, right_idx+1)]

