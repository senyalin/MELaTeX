"""
Given the MEHSGroup, which don't overlap horizontally conceptually.

"""

from pdfxml.me_layout.layout_configuration.constraints.constraint_module import create_constraints_for_mg_list
from pdfxml.me_layout.layout_prediction.exp_common import predict_with_elems_constraints
from pdfxml.me_layout.me_group.enclosed_me_group import MERadicalGroup, MEFenceGroup
from pdfxml.me_layout.me_group.vertical_me_group import MESupSubGroup, MEBindVarGroup, MEFractionGroup, MEAccentGroup, \
    MEUpperGroup, MEUnderGroup, GridGroup
from pdfxml.me_layout.me_group.internal_me_group import MEHorSupOrSubGroup
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath, MEHSSGroup
from pdfxml.me_layout.me_group.hor_me_group import MESubGroup, MESupGroup, MEHorGroup
from pdfxml.me_layout.pss_exp.pss_exception import NoneMEGroupException
from pdfxml.me_layout.script_config2me_group import script_config2me_group


def recursive_organize_sup_or_sub_in_hs_group(mg, pred_sc_func=None, debug=False):
    """
    recursively work on the MEHorSupOrSubGroup
    should not have UnorganizedGroupPath

    The core of the function call is organize_sup_or_sub_in_hs_group,
    the recursive process is designed to find MEHorSupOrSubGroup in the recursive hierarchy

    :param mg:
    :param pred_sc_func:
    :return:
    """

    # considering different conditions
    assert not isinstance(mg, UnorganizedGroupPath)
    if isinstance(mg, MEAccentGroup):
        ":type ugp: MEHatGroup"
        mg.me_group = recursive_organize_sup_or_sub_in_hs_group(mg.me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MERadicalGroup):
        ":type ugp: MESqrtGroup"
        mg.me_group = recursive_organize_sup_or_sub_in_hs_group(mg.me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MEFractionGroup):
        mg.down_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.down_me_group, pred_sc_func, debug=debug)
        mg.up_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.up_me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MEBindVarGroup):
        mg.down_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.down_me_group, pred_sc_func, debug=debug)
        mg.up_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.up_me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MEHorSupOrSubGroup):
        ":type mg: MEHorSupOrSubGroup"
        mg = organize_sup_or_sub_in_hs_group(mg, pred_sc_func, debug=debug)

        # indeed cause a bug, if dont' go deeper
        new_me_groups = []
        for child_me_group in mg.me_groups:
            new_me_groups.append(
                recursive_organize_sup_or_sub_in_hs_group(child_me_group, pred_sc_func, debug=debug)
            )
        mg.me_groups = new_me_groups

        return mg
    elif isinstance(mg, MESymbolGroup):
        return mg
    elif isinstance(mg, MESupGroup):
        mg.base_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.base_me_group, pred_sc_func, debug=debug)
        mg.sup_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.sup_me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MESubGroup):
        mg.base_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.base_me_group, pred_sc_func, debug=debug)
        mg.sub_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.sub_me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MESupSubGroup):
        mg.base_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.base_me_group, pred_sc_func, debug=debug)
        mg.sup_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.sup_me_group, pred_sc_func, debug=debug)
        mg.sub_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.sub_me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MEHorGroup):
        """
        NOTE, somehow, the me_groups under it needs to be re-organized
        """
        new_me_groups = []
        for child_me_group in mg.me_groups:
            new_me_groups.append(
                recursive_organize_sup_or_sub_in_hs_group(child_me_group, pred_sc_func, debug=debug)
            )
        mg.me_groups = new_me_groups
        return mg
    elif isinstance(mg, MEFenceGroup):
        mg.hs_group = recursive_organize_sup_or_sub_in_hs_group(mg.hs_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, EmptyGroup):
        return mg
    elif mg is None:
        raise NoneMEGroupException()
    elif isinstance(mg, MEHSSGroup):
        raise Exception("TODO MEHSSGroup should not occur here")
    elif isinstance(mg, MEUpperGroup):
        # NOTE, very important to recursively pass the pred function here
        mg.base_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.base_me_group, pred_sc_func, debug=debug)
        mg.upper_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.upper_me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, MEUnderGroup):
        # NOTE, very important to recursively pass the pred function here
        mg.base_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.base_me_group, pred_sc_func, debug=debug)
        mg.under_me_group = recursive_organize_sup_or_sub_in_hs_group(mg.under_me_group, pred_sc_func, debug=debug)
        return mg
    elif isinstance(mg, GridGroup):
        for r in range(len(mg.mg_mat)):
            for c in range(len(mg.mg_mat[r])):
                mg.mg_mat[r][c] = recursive_organize_sup_or_sub_in_hs_group(mg.mg_mat[r][c], pred_sc_func, debug=debug)
        return mg
    else:
        print mg, type(mg)
        raise Exception("Unknown type")


# TODO, what does pred_sc_func mean?
def organize_sup_or_sub_in_hs_group(hs_group, pred_sc_func=None, debug=False):
    """

    :param hs_group:
    :param pred_sc_func:
    :return:
    """
    assert isinstance(hs_group, MEHorSupOrSubGroup)

    # create constraints and configurations
    constraints = create_constraints_for_mg_list(hs_group.me_groups)

    # evaluate the most proper configuration
    if pred_sc_func is None:
        script_config = predict_with_elems_constraints(hs_group.me_groups, constraints, debug=debug)
    else:
        script_config = pred_sc_func(
            hs_group.me_groups,
            constraints=constraints,
            debug=debug)

    # reconstruct the hierarchy based on the script_config
    # no sup/sub at the same time.
    hs_group = script_config2me_group(script_config, hs_group.me_groups)
    return hs_group
