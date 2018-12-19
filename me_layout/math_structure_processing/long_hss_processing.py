"""

"""
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.hor_me_group import MEHorGroup
from pdfxml.me_layout.me_group.internal_me_group import MEHSSGroup, MEHorSupOrSubGroup
from pdfxml.me_layout.me_group.vertical_me_group import MESupSubGroup, MEBindVarGroup, MEFractionGroup, MEAccentGroup, \
    MEUpperGroup, MEUnderGroup, GridGroup
from pdfxml.me_layout.me_group.enclosed_me_group import MERadicalGroup, MEFenceGroup
from pdfxml.me_layout.pss_exp.pss_exception import NoneMEGroupException

len_thres = 15


def split_long_in_hsos_2parts(hs_group):
    """
    split into 2 parts

    :param hs_group:
    :return:
    """
    assert isinstance(hs_group, MEHorSupOrSubGroup)

    new_me_groups = [recursive_long_hss(mg) for mg in hs_group.me_groups]
    hs_group.me_groups = new_me_groups

    if len(hs_group.me_groups) < len_thres:
        return hs_group

    hs_group.me_groups.sort(key=lambda mg: mg.get_tight_bbox().left())  # organize from left to right

    from pdfxml.me_layout.math_structure_processing.me_struct_inspection.long_me_split2 import get_split_idx

    # get the split index, which is with the largest height
    split_idx = get_split_idx(hs_group.me_groups)
    if split_idx == -1:
        print 'could not further split, leave it as it is'
        return hs_group

    me_groups1 = hs_group.me_groups[:split_idx]
    me_groups2 = hs_group.me_groups[split_idx:]
    if len(me_groups1) == 0 or len(me_groups2) == 0:
        raise Exception("should not be empty for one of them")
    else:
        nmg1 = MEHorSupOrSubGroup(me_groups1)
        nmg2 = MEHorSupOrSubGroup(me_groups2)
        rmg = MEHorGroup([nmg1, nmg2])
        rmg = recursive_long_hss(rmg)
        return rmg


def split_long_in_hsos(hs_group):
    """
    for now, use the version that split into two parts

    :param hs_group:
    :return:
    """
    return split_long_in_hsos_2parts(hs_group)


def recursive_long_hss(mg):
    """

    :param mg:
    :return:
    """
    if isinstance(mg, MESymbolGroup):
        return mg
    elif isinstance(mg, MEBindVarGroup):
        mg.up_me_group = recursive_long_hss(mg.up_me_group)
        mg.down_me_group = recursive_long_hss(mg.down_me_group)
        return mg
    elif isinstance(mg, MEFractionGroup):
        mg.up_me_group = recursive_long_hss(mg.up_me_group)
        mg.down_me_group = recursive_long_hss(mg.down_me_group)
        return mg
    elif isinstance(mg, MEAccentGroup):
        mg.me_group = recursive_long_hss(mg.me_group)
        return mg
    elif isinstance(mg, MEHorSupOrSubGroup):
        return split_long_in_hsos(mg)
    elif isinstance(mg, MEFenceGroup):
        mg.hs_group = recursive_long_hss(mg.hs_group)
        return mg
    elif isinstance(mg, MESupSubGroup):
        mg.base_me_group = recursive_long_hss(mg.base_me_group)
        mg.sup_me_group = recursive_long_hss(mg.sup_me_group)
        mg.sub_me_group = recursive_long_hss(mg.sub_me_group)
        return mg
    elif isinstance(mg, EmptyGroup):
        return mg
    elif isinstance(mg, MEHSSGroup):
        # TODO, NOTE, there might introduce some error here.
        raise Exception("should not have such?")
    elif isinstance(mg, MERadicalGroup):
        mg.me_group = split_long_in_hsos(mg.me_group)
        return mg
    elif mg is None:
        raise NoneMEGroupException()
    elif isinstance(mg, MEHorGroup):
        """
        NOTE, somehow, the me_groups under it needs to be re-organized
        """
        new_me_groups = []
        for child_me_group in mg.me_groups:
            new_me_groups.append(recursive_long_hss(child_me_group))
        mg.me_groups = new_me_groups
        return mg
    elif isinstance(mg, MEUpperGroup) or isinstance(mg, MEUnderGroup):
        # less likely to have long things
        return mg
    elif isinstance(mg, GridGroup):
        return mg
    else:
        print "recursive_organize_fence_in_hs_group", type(mg)
        raise Exception("TODO")


