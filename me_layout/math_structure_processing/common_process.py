

def seperate_me_group(me_groups, i, j, ignore_list=[]):
    """

    :param me_groups:
    :param i: start fence
    :param j: close fence
    :return:
    """
    in_fence_me_groups = []
    out_fence_me_groups = []

    open_fence_me_group = me_groups[i]
    ":type open_fence_me_group: MESymbolGroup"
    close_fence_me_group = me_groups[j]
    ":type close_fence_me_group: MESymbolGroup"

    # TODO, make this a common function
    for k, me_group2 in enumerate(me_groups):
        if k == i or k == j or k in ignore_list:
            continue
        else:
            # check whether in the range or not
            # vertical overlapping
            #open_right = me_group2.left() + me_group2.width() * 0.1 > open_fence_me_group.right() - open_fence_me_group.width() * 0.1
            #close_left = me_group2.right() - me_group2.width() * 0.1 < close_fence_me_group.left() + close_fence_me_group.width() * 0.1
            open_right = me_group2.get_tight_bbox().h_center() > open_fence_me_group.get_tight_bbox().h_center()
            close_left = me_group2.get_tight_bbox().h_center() < close_fence_me_group.get_tight_bbox().h_center()

            if open_fence_me_group.v_overlap(me_group2) and open_right and close_left:
                in_fence_me_groups.append(me_group2)
            else:
                out_fence_me_groups.append(me_group2)

    return in_fence_me_groups, out_fence_me_groups
