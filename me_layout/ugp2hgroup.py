"""
Convert from UGP to HGroup
"""
from pdfxml.me_layout.math_structure_processing.long_hss_processing import recursive_long_hss
from pdfxml.me_layout.math_structure_processing.func_process import recursive_organize_func_in_hs_group
from pdfxml.me_layout.math_structure_processing.fence_process import recursive_organize_fence_in_hs_group
from pdfxml.me_layout.math_structure_processing.sup_sub_process import recursive_organize_subandsup
from pdfxml.me_layout.math_structure_processing.bind_var_op_process import organize_bind_var_in_ugp
from pdfxml.me_layout.math_structure_processing.fraction_process import organize_fraction_in_ugp
from pdfxml.me_layout.math_structure_processing.hat_process import organize_hat_in_ugp
from pdfxml.me_layout.math_structure_processing.radical_process import organize_sqrt_in_ugp
from pdfxml.me_layout.math_structure_processing.sup_or_sub_process import recursive_organize_sup_or_sub_in_hs_group
from pdfxml.me_layout.math_structure_processing.ugp_hss_process import recursive_ugp_hss
from pdfxml.me_layout.pss_exp.test_infty_cdb_parametric import predict_with_elems_constraints_parametric_consecutive


def ugp2hgroup(ugp, pred_func=predict_with_elems_constraints_parametric_consecutive):
    """
    This is an interface to calculate the ME layout from
    UnorganizedGroupPath

    :param ugp:
    :type ugp: UnorganizedGroupPath
    :param pred_func:
        the default function to resolve the script relationship
        if value equals "norun", then just skip the last step
    :return:
    """

    # through pipeline as draw in the workflow
    organize_hat_in_ugp(ugp)
    organize_sqrt_in_ugp(ugp)
    organize_fraction_in_ugp(ugp)
    organize_bind_var_in_ugp(ugp)
    assert len(ugp.me_paths) == 0

    # TODO, recursive convert UGP to HSS
    hss_group = recursive_ugp_hss(ugp)  # no vertical relation at each level
    hs_group = recursive_organize_subandsup(hss_group)

    ":type hs_group: MEHorSupOrSubGroup"
    hs_group = recursive_organize_fence_in_hs_group(hs_group)

    # TODO, call the recursive_organize_func_in_hs_group(hs_group)
    hs_group = recursive_organize_func_in_hs_group(hs_group)
    hs_group = recursive_long_hss(hs_group)

    # recursively apply the processing until all changed to MEHorGroup
    if pred_func != "norun":
        h_group = recursive_organize_sup_or_sub_in_hs_group(hs_group, pred_func)
        return h_group
    return hs_group
