"""
Find the matched fence will convert the problem into two sub problems:
1. sub problem 1 of within fence analysis
2. sub problem 2 of the whole ME, but treating fence as a unit

further the fence symbols themselve would also be ignored

it's intuitively designed as follows:
in each iteration,
find pair of left parenthesis and right parenthesis, overlap vertically
that don't have other parenthesis in between vertically overlapping
"""
from pdfxml.pdf_util.unionfind import UnionFind
from pdfxml.pdf_util.layout_util import merge_bbox_list
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.internal_me_group import MEHSSGroup, MEHorSupOrSubGroup
from pdfxml.me_layout.me_group.hor_me_group import MESubGroup, MESupGroup, MEHorGroup
from pdfxml.me_layout.me_group.vertical_me_group import MESupSubGroup, MEBindVarGroup, MEFractionGroup, MEAccentGroup, \
    MEUnderGroup, MEUpperGroup, MEUpperUnderGroup, GridGroup
from pdfxml.me_layout.me_group.enclosed_me_group import MERadicalGroup, MEFenceGroup
from pdfxml.me_layout.pss_exp.pss_exception import NoneMEGroupException, ComponentEmptyException
from pdfxml.me_layout.math_structure_processing.vert_fence_process import organize_vert_in_hs_group
from pdfxml.me_layout.math_structure_processing.common_process import seperate_me_group


fence_open2close = {
    "(": ")",
    "[": "]",
    "{": "}",
    #"|": "|" # could not pair them very well
    "langle": "rangle",
    "lfloor": "rfloor",
}


def is_open_fence(latex_val):
    """

    :param latex_val: string of latex symbol
    :return:
    """
    return latex_val in fence_open2close


def get_matched_close_fence(latex_val):
    """

    :param latex_val:
    :return:
    """
    assert latex_val in fence_open2close
    return fence_open2close[latex_val]


def recursive_organize_fence_in_hs_group(mg):
    """
    recursively organize the fence
    :param mg:
    :return:
    """
    if isinstance(mg, MESymbolGroup):
        return mg
    elif isinstance(mg, MEBindVarGroup):
        mg.up_me_group = recursive_organize_fence_in_hs_group(mg.up_me_group)
        mg.down_me_group = recursive_organize_fence_in_hs_group(mg.down_me_group)
        return mg
    elif isinstance(mg, MEFractionGroup):
        mg.up_me_group = recursive_organize_fence_in_hs_group(mg.up_me_group)
        mg.down_me_group = recursive_organize_fence_in_hs_group(mg.down_me_group)
        return mg
    elif isinstance(mg, MEAccentGroup):
        mg.me_group = recursive_organize_fence_in_hs_group(mg.me_group)
        return mg
    elif isinstance(mg, MEHorSupOrSubGroup):
        return organize_fence_in_hs_group(mg)
    elif isinstance(mg, MEFenceGroup):
        mg.hs_group = organize_fence_in_hs_group(mg.hs_group)
        return mg
    elif isinstance(mg, MESupSubGroup):
        mg.base_me_group = recursive_organize_fence_in_hs_group(mg.base_me_group)
        mg.sup_me_group = recursive_organize_fence_in_hs_group(mg.sup_me_group)
        mg.sub_me_group = recursive_organize_fence_in_hs_group(mg.sub_me_group)
        return mg
    elif isinstance(mg, EmptyGroup):
        return mg
    elif isinstance(mg, MEHSSGroup):
        return mg
    elif isinstance(mg, MERadicalGroup):
        mg.me_group = recursive_organize_fence_in_hs_group(mg.me_group)
        return mg
    elif mg is None:
        raise NoneMEGroupException()
    elif isinstance(mg, MEHorGroup):
        #organize_fence_in_hs_group(mg)
        pass
        return mg
    elif isinstance(mg, MEUnderGroup):
        mg.base_me_group = recursive_organize_fence_in_hs_group(mg.base_me_group)
        mg.under_me_group = recursive_organize_fence_in_hs_group(mg.under_me_group)
        return mg
    elif isinstance(mg, MEUpperGroup):
        mg.base_me_group = recursive_organize_fence_in_hs_group(mg.base_me_group)
        mg.upper_me_group = recursive_organize_fence_in_hs_group(mg.upper_me_group)
        return mg
    elif isinstance(mg, MEUpperUnderGroup):
        mg.base_me_group = recursive_organize_fence_in_hs_group(mg.base_me_group)
        mg.upper_me_group = recursive_organize_fence_in_hs_group(mg.upper_me_group)
        mg.under_me_group = recursive_organize_fence_in_hs_group(mg.under_me_group)
        return mg
    else:
        print "recursive_organize_fence_in_hs_group", type(mg)
        raise Exception("TODO")


def organize_fence_in_hs_group(hs_group):
    """
    # TODO, this part need to be recursive

    :param hs_group: process to group the parenthesis
    :type hs_group: MEHorSupOrSubGroup
    :return:
    """
    """
    assert isinstance(hs_group, MEHorSupOrSubGroup) or isinstance(hs_group, MEHorGroup)
    if isinstance(hs_group, MEHorGroup) and len(hs_group.me_groups) == 3 and str(hs_group.me_groups[0]).startswith("||") and str(hs_group.me_groups[2]).startswith("||"):
        hs_group.me_groups = [recursive_organize_fence_in_hs_group(me_group) for me_group in hs_group.me_groups]
    else:
        hs_group.me_groups = [recursive_organize_fence_in_hs_group(me_group) for me_group in hs_group.me_groups]
    """
    if not isinstance(hs_group, MEHorSupOrSubGroup):
        print type(hs_group)

    assert isinstance(hs_group, MEHorSupOrSubGroup) or isinstance(hs_group, GridGroup)

    if isinstance(hs_group, EmptyGroup):
        return hs_group
    if isinstance(hs_group, GridGroup):
        # shold have the sub fence ready by now.
        for r in range(len(hs_group.mg_mat)):
            for c in range(len(hs_group.mg_mat[r])):
                hs_group.mg_mat[r][c] = organize_fence_in_hs_group(hs_group.mg_mat[r][c])
        return hs_group

    # separate the core from the above logic.
    # as when constructing MEGroup from the inftyCDB ground truth,
    # need to recover the fence structure from the MEHorGroup

    return organize_fence_core(hs_group)


def is_open_fence_me_group(mg):
    """
    still as the old version,
    don't have the issue as the is_closed_fence_me_group

    :param mg:
    :return:
    """
    if isinstance(mg, MESymbolGroup):
        return is_open_fence(mg.me_symbol.latex_val)
    return False


def is_closed_fence_me_group(mg):
    """
    When from font setting to ME layout, the sub/sup is resolve at last, then simply look for MESymbol

    But when built from the ground truth of the InftyCDB, the sub/sup is first recovered, and then resolve the fence
    This means the closed symbol could also attached with sup , sub, or sup sub

    :param mg:
    :return:
    """
    if isinstance(mg, MESymbolGroup):
        return mg.me_symbol.latex_val in fence_open2close.values()
    elif isinstance(mg, MESupSubGroup) or isinstance(mg, MESubGroup) or isinstance(mg, MESupGroup):
        return is_closed_fence_me_group(mg.base_me_group)
    return False


def get_fence_val_from_me_group(mg):
    if isinstance(mg, MESymbolGroup):
        return mg.me_symbol.latex_val
    elif isinstance(mg, MESupSubGroup) or isinstance(mg, MESubGroup) or isinstance(mg, MESupGroup):
        return get_fence_val_from_me_group(mg.base_me_group)
    else:
        raise Exception("Not fence")


def is_matched_fence_me_group(mg1, mg2):
    """

    :param mg1:
    :param mg2:
    :return:
    """
    if is_open_fence_me_group(mg1) and is_closed_fence_me_group(mg2):
        return get_fence_val_from_me_group(mg2) == fence_open2close[get_fence_val_from_me_group(mg1)]
    return False


def is_grid_me_group(mg_list):
    """
    if vertically non overlapping,
    and horizontally non overlapping.

    :param mg_list:
    :return:
    """
    print("Might mistakenly treat upper/under as one line")
    # TODO, later
    # if there is big operator here, stop
    uf = UnionFind()
    for i, mg_i in enumerate(mg_list):
        for j, mg_j in enumerate(mg_list):
            if not j > i:
                continue
            if mg_i.get_tight_bbox().v_overlap(mg_j.get_tight_bbox()):
                uf.merge(i, j)

    idx_group_list = uf.get_groups()
    if len(idx_group_list) <= 1:
        return False

    # then look for the horizontal split
    # might have empty Expression here.
    return True


def create_grid_me_group(mg_list):
    """

    :param mg_list:
    :return:
    """
    # first, is the vertical separation
    v_uf = UnionFind()
    h_uf = UnionFind()
    for i, mg_i in enumerate(mg_list):
        for j, mg_j in enumerate(mg_list):
            if not j > i:
                continue
            if mg_i.get_tight_bbox().v_overlap(mg_j.get_tight_bbox()):
                v_uf.merge(i, j)
            if mg_i.get_tight_bbox().h_overlap(mg_j.get_tight_bbox()):
                h_uf.merge(i, j)

    v_idx_group_list = v_uf.get_groups()
    assert(len(v_idx_group_list) > 1)
    # second, is the horizontal separation
    v_bbox_list = []
    for v_idx_group in v_idx_group_list:
        v_bbox_list.append(
            merge_bbox_list([mg_list[v_idx].get_tight_bbox() for v_idx in v_idx_group])
        )
    v_bbox_list.sort(key=lambda bbox:-bbox.top())

    h_idx_group_list = h_uf.get_groups()
    h_bbox_list = []
    for h_idx_group in h_idx_group_list:
        h_bbox_list.append(
            merge_bbox_list([mg_list[h_idx].get_tight_bbox() for h_idx in h_idx_group])
        )
    h_bbox_list.sort(key=lambda bbox: bbox.left())

    mg_mat = []
    for r in range(len(v_bbox_list)):
        mg_mat.append([])
        for c in range(len(h_bbox_list)):
            mg_mat[r].append([])
            for mg in mg_list:
                if v_bbox_list[r].v_overlap(mg.get_tight_bbox()) \
                        and h_bbox_list[c].h_overlap(mg.get_tight_bbox()):
                    mg_mat[r][c].append(mg)
    mhss_mat = []
    for r, mg_list in enumerate(mg_mat):
        mhss_mat.append([])
        for c in range(len(mg_mat[r])):
            if len(mg_mat[r][c]) > 0:
                mhss_mat[r].append(MEHorSupOrSubGroup(mg_mat[r][c]))
            else:
                mhss_mat[r].append(EmptyGroup())

    return GridGroup(mhss_mat)
    #return mg_mat


def organize_fence_core(hs_group, recursive_func=None, in_fence_class=MEHorSupOrSubGroup, do_vert_bar=True):
    """

    the logic here is to find the pairing of fences iteratively.

    :param do_vert_bar:
        set default as true in the general processing,
        but in the structure reconstruction from the ground truth, skip this as some error might be induced.
    :param recursive_func: the recursive function call to recursive traverse all elements in the hierachy
    :param hs_group: could be MEHorGroup, or any structure with me_groups member variable
    :return:
    """
    if recursive_func is None:
        recursive_func = recursive_organize_fence_in_hs_group
    # for the construction from inftycdb
    hs_group.me_groups = [recursive_func(me_group) for me_group in hs_group.me_groups]

    hs_group.me_groups.sort(key=lambda me_group: me_group.left())
    while True:
        paired_fence_detected = False
        for i, me_group in enumerate(hs_group.me_groups):
            if not isinstance(me_group, MESymbolGroup): # TO ensure all element will be processed for fence matching
                hs_group.me_groups[i] = recursive_func(me_group)
                continue # if not as MESymbolGroup, then could not be open fence, just skip current position for possible fence

            if is_open_fence_me_group(me_group):
                # find the ")" and keep everything in between
                close_fence_idx, met_another_open_fence = -1, False
                for j in range(i+1, len(hs_group.me_groups)):
                    # there are two possibilities here,
                    # 1. not open fence or closed fence, just pass
                    # 2. a matched close fence, store the closed fence index, and break
                    # 3. meet another open fence before meeting a closed fence, then ignore the current fence, stop looking for matched close fence
                    if is_open_fence_me_group(hs_group.me_groups[j]):
                        met_another_open_fence = True
                        break
                    if is_closed_fence_me_group(hs_group.me_groups[j]) and \
                            is_matched_fence_me_group(hs_group.me_groups[i], hs_group.me_groups[j]):
                        close_fence_idx = j
                        break

                if met_another_open_fence:
                    continue

                if close_fence_idx != -1:
                    # create MEFenceGroup here
                    paired_fence_detected = True

                    in_fence_me_groups, out_fence_me_groups = seperate_me_group(hs_group.me_groups, i, j)
                    # TODO, group the in_fence_me_groups into grid if possible for matrix

                    open_fence_me_group, close_fence_me_group = hs_group.me_groups[i], hs_group.me_groups[j]
                    ":type open_fence_me_group: MESymbolGroup"
                    ":type close_fence_me_group: MESymbolGroup"

                    if len(in_fence_me_groups) == 0:
                        raise ComponentEmptyException()

                    # NOTE, this is another difference
                    if is_grid_me_group(in_fence_me_groups):
                        in_hs_group = create_grid_me_group(in_fence_me_groups)
                    else:
                        in_hs_group = in_fence_class(in_fence_me_groups)

                    # TODO, if both are MESymbol Group, then good
                    # else need to based on the close group, to create the corresponding me_fence_group and even sup/sub group
                    if isinstance(close_fence_me_group, MESymbolGroup):
                        me_fence_group = MEFenceGroup(
                            in_hs_group,
                            open_fence_me_group.me_symbol,
                            close_fence_me_group.me_symbol)
                        out_fence_me_groups.append(me_fence_group)
                    elif isinstance(close_fence_me_group, MESupGroup) or isinstance(close_fence_me_group, MESubGroup) or \
                            isinstance(close_fence_me_group, MESupSubGroup):
                        me_fence_group = MEFenceGroup(
                            in_hs_group,
                            open_fence_me_group.me_symbol,
                            close_fence_me_group.base_me_group.me_symbol
                        )
                        # just assign the new MEFenceGroup as the base
                        close_fence_me_group.base_me_group = me_fence_group
                        out_fence_me_groups.append(close_fence_me_group)
                    else:
                        raise Exception("Unknown close fence ME Group type")

                    out_fence_me_groups.sort(key=lambda me_group: me_group.left())  # re-order the element
                    hs_group.me_groups = out_fence_me_groups
                    paired_fence_detected = True
                    break
                else:
                    # might be piece wise ME here.

                    # the open fence here
                    # the groups on it's right
                    piecewise_group = create_piecewise(hs_group.me_groups[i], hs_group.me_groups[i+1:])
                    if piecewise_group is not None:
                        out_fence_me_groups = hs_group.me_groups[:i]
                        out_fence_me_groups.append(piecewise_group)
                        hs_group.me_groups = out_fence_me_groups
                        paired_fence_detected = True
                        break

        # the while loop here
        if not paired_fence_detected:
            break

    if do_vert_bar:
        hs_group = organize_vert_in_hs_group(hs_group)
    return hs_group


def create_piecewise(open_fence_symbol, right_me_groups):
    """

    :param open_fence_symbol:
    :param right_me_groups: all the me groups on its right
    :return:
    """
    # check everything overlap
    for right_mg in right_me_groups:
        assert open_fence_symbol.get_tight_bbox().v_overlap(right_mg.get_tight_bbox())

    # do groupping by vertical overlapping
    uf = UnionFind()
    for i, mg_i in enumerate(right_me_groups):
        for j, mg_j in enumerate(right_me_groups):
            if not j> i:
                continue
            if mg_i.get_tight_bbox().v_overlap(mg_j.get_tight_bbox()):
                uf.merge(i, j)

    # then do it recursively for the fence processing
    idx_group_list = uf.get_groups()
    if len(idx_group_list) <= 1:
        return None

    bbox_list = []
    for idx_group in idx_group_list:
        bbox_list.append(
            merge_bbox_list([right_me_groups[idx].get_tight_bbox() for idx in idx_group])
        )
    bbox_list.sort(key=lambda bbox: -bbox.top())

    mg_list_list = []
    for bbox in bbox_list:
        tmp_mg_list = []
        for mg in right_me_groups:
            if mg.get_tight_bbox().v_overlap(bbox):
                tmp_mg_list.append(mg)
        mg_list_list.append(tmp_mg_list)

    mhss_list = []
    for mg_list in mg_list_list:
        mhss = MEHorSupOrSubGroup(mg_list)
        mhss = recursive_organize_fence_in_hs_group(mhss)
        mhss_list.append([mhss])

    gg = GridGroup(mhss_list)
    # might only have half fence
    return MEFenceGroup(gg, open_fence_symbol)
