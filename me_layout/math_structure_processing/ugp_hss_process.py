from pdfxml.me_layout.me_group.vertical_me_group import MEBindVarGroup, MEFractionGroup, MEAccentGroup
from pdfxml.me_layout.me_group.enclosed_me_group import MERadicalGroup
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.hor_me_group import MEHorGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath, MEHSSGroup


def recursive_ugp_hss(mg):
    """

    :param mg: an unorganizedGroupPath after hat, sqrt, fraction, bind var processing
    :type mg: MEGroup
    :return:
    :rtype: MEHSSGroup
    """
    if isinstance(mg, UnorganizedGroupPath):
        # TODO, additional checking and assertion
        new_me_groups = []
        for me_group in mg.me_groups:
            new_me_groups.append(recursive_ugp_hss(me_group))
        return MEHSSGroup(new_me_groups)
    elif isinstance(mg, MEAccentGroup):
        ":type ugp: MEHatGroup"
        mg.me_group = recursive_ugp_hss(mg.me_group)
        assert not isinstance(mg.me_group, UnorganizedGroupPath)
        return mg
    elif isinstance(mg, MERadicalGroup):
        ":type ugp: MESqrtGroup"
        mg.me_group = recursive_ugp_hss(mg.me_group)
        return mg
    elif isinstance(mg, MEFractionGroup):
        mg.down_me_group = recursive_ugp_hss(mg.down_me_group)
        mg.up_me_group = recursive_ugp_hss(mg.up_me_group)
        return mg
    elif isinstance(mg, MEBindVarGroup):
        mg.down_me_group = recursive_ugp_hss(mg.down_me_group)
        mg.up_me_group = recursive_ugp_hss(mg.up_me_group)
        return mg
    elif isinstance(mg, MESymbolGroup):
        return mg
    elif isinstance(mg, MEHSSGroup):
        return mg
    elif isinstance(mg, EmptyGroup):
        # This is called from the MEBindVarGroup, that there is no upper bound part,
        # so just call it as EmptyGroup
        # when an empty group is created?
        return mg
    elif isinstance(mg, MEHorGroup):
        return mg
        # might be from the function mering process.
    else:
        print type(mg)
        raise Exception("Unknown type")
