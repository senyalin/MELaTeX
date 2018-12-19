"""
parametric model based on phyical modeling
"""
import numpy as np
from pdfxml.me_layout.layout_configuration.constraints.constraint_module import constraint_sat_for_config_for_must_hor
from pdfxml.pdf_util.bbox import BBox
from pdfxml.me_layout.layout_configuration.line_configuration import enumerate_configuration
from pdfxml.me_layout.layout_configuration.line_configuration_with_element import \
    enumerate_configuration_with_elements
from pdfxml.me_layout.layout_prediction.pos_features import height_ratio_AB, normalized_ycenter_diff_AB
from pdfxml.me_layout.pss_exp.pss_exception import TooLongException
from pdfxml.me_layout.pss_model.pss_dist_hr import get_pss_hr_dist
from pdfxml.me_layout.pss_model.pss_dist_nvcd import get_pss_nvcd_dist
from pdfxml.me_layout.math_structure_processing.long_hss_processing import len_thres


# TODO, move the following import
def get_param_hr_dist(rel_list):
    """

    :param rel_list:
    :return:
    """
    return get_pss_hr_dist(rel_list)


def get_param_nvcd_dist(rel_list):
    return get_pss_nvcd_dist(rel_list)


def get_param_dist(rel_list, fea_name):
    """
    hr: h2/h1
    nvcd: (c2-c1)/h1

    :param rel_list: list of id of relations
    :param fea_name: hr or nvcd
    :return:
    """
    if fea_name == "hr":
        return get_param_hr_dist(rel_list)
    elif fea_name in ["nvcd", "nycd"]:  # normalized center difference
        return get_param_nvcd_dist(rel_list)
    else:
        raise Exception("unsupported feature {}".format(fea_name))


# TODO, set debug as True to understand the speed
# change back to false now.
def predict_with_elems_constraints_parametric_consecutive(element_list, constraints=None):
    """
    each elem is describe the value, and the bounding box
    It is assumed that the element list are ordered from left to right
    There is no vertical overlapping

    The inference here is not based on the parametric modeling of the shift and scaling
    Besides, there is no need for enumerate all pairs of element,
    as the free variable is limited, and only are the consecutive pairs

    NOTE: if in debug mode, a ground truth will be assigned manually.
    Only the detail of the one with the highest score and the ground truth are printed out.

    :param element_list: list of me groups
    :type element_list: list[MEGroup]
    :param constraints:
        constraints is passed to this function,
         not generated within
    :return:
    :rtype: ScriptConfig
    """
    # enumerate all possible configuration
    print 'try to create config for {} amount of elemnts'.format(len(element_list))

    # NOTE, increase a bit to discover the program bugs
    # change this to a small one
    if len(element_list) > len_thres:
        raise TooLongException(len(element_list))
    import pdfxml.me_layout.me_layout_config as me_layout_config
    if me_layout_config.OPTION_A_4_LOCAL_CONFIG_BY_CENTER:
        config_list = enumerate_configuration_with_elements(element_list, constraints)
        # only get the old ones when test the comparison
        print 'new size', len(config_list)
    else:
        config_list = enumerate_configuration(len(element_list), constraints)

    if len(config_list) == 0:
        raise Exception("no possible configurations")

    gd_sc = None

    # adjust the bbox here
    from pdfxml.me_layout.char_adjust_bbox_core import could_estimate_height, could_calculate_center
    adjusted_bbox_list = [element.get_adjusted_bbox() for element in element_list]
    is_regular_list = []
    for element in element_list:
        baseline_symbol = element.get_baseline_symbol()
        is_regular_list.append(could_estimate_height(baseline_symbol))
    could_calculate_center_list = []
    for element in element_list:
        baseline_symbol = element.get_baseline_symbol()
        could_calculate_center_list.append(could_calculate_center(baseline_symbol))

    # for each configuration, generate the paired relation for all pairs
    # TODO, later
    # constraint_id_list = [c['id'] for c in constraints]

    # remove the common among different configurations
    config2org_pair_rel_set = {}
    for config in config_list: # ScriptConfig type
        # NOTE, enumerating all might improve the performance.
        pair_rel_set = set(config.get_pair_rel_list(me_groups=element_list))
        config2org_pair_rel_set[config] = pair_rel_set

    config2reduced_pair_rel_set = config2org_pair_rel_set

    post_check_config_list = []
    for sc in config_list:
        if not constraint_sat_for_config_for_must_hor(sc, constraints):
            continue
        post_check_config_list.append(sc)

    config_list = post_check_config_list

    log_sum_list = []
    max_log_sum = -1000000
    for config in config_list: # ScriptConfig type

        pair_rel_set = config2reduced_pair_rel_set[config]
        log_sum = 0.
        is_gd_config = False

        for pair_rel in pair_rel_set:
            # for each pair, evaluate the probability and sum of log
            i, j, rel_list = pair_rel

            if isinstance(adjusted_bbox_list[i], BBox):
                hr = height_ratio_AB(adjusted_bbox_list[i].quadruple, adjusted_bbox_list[j].quadruple)
                nycd = normalized_ycenter_diff_AB(adjusted_bbox_list[i].quadruple, adjusted_bbox_list[j].quadruple)
            else:
                hr = height_ratio_AB(adjusted_bbox_list[i], adjusted_bbox_list[j])
                nycd = normalized_ycenter_diff_AB(adjusted_bbox_list[i], adjusted_bbox_list[j])

            hr_dist = get_param_dist(rel_list, "hr")
            nycd_dist = get_param_dist(rel_list, "nycd")
            hr_pdf_val = hr_dist.pdf(hr)
            nycd_pdf_val = nycd_dist.pdf(nycd)

            # might be slow here possible because of load the pdf each time
            # the hr is added if both of them are regular shaped symbol
            # the nycd is added if the base is regular shaped symbol, and the second is centered symbol
            import pdfxml.me_layout.me_layout_config as me_layout_config
            if me_layout_config.disable_hr_nvcd_for_non_regular:
                # if both regular, then good
                if is_regular_list[i] and is_regular_list[j]:
                    log_sum += np.log(hr_pdf_val)
                    log_sum += np.log(nycd_pdf_val)
                elif is_regular_list[i] and could_calculate_center_list[j]:
                    log_sum += np.log(nycd_pdf_val)
                else:
                    pass
            else:
                log_sum += np.log(hr_pdf_val)
                log_sum += np.log(nycd_pdf_val)

        if log_sum > max_log_sum:
            max_log_sum = log_sum
        log_sum_list.append(log_sum)

    max_idx = np.argmax(log_sum_list)
    return config_list[int(max_idx)] #JASON MODIFICATION!!!


def test_parametric_model():
    """
    Find a simple cases

    :return:
    """
    test_me_idx_list = [
        28000767,  # B_{\alpha}
        28005929,  # $\mathfrak{H}_{0}$
        28001483,  # $v_{\lambda}$. bug of lambda part
        28000716,  # $P_{n-q-1}^{\alpha,-n}$ sub_sup
        28000006,  # $(-\rho)^{\alpha},\alpha>0$, hor_sup
        28000918,  # $g=a+\mathrm{d}\overline{\xi}\wedge b$,
        28000118,  # $A^{2}$
        28000226,  # $f,1\leq q\leq n-1$,
        28000882,  # $F(m,b,c,z)$
        28000349,  # $g,\overline{\partial}g\in L_{\alpha}^{2}$.

        28000982,  # $\partial K_{\alpha}=-K_{\alpha+1}\partial$
        28000627  # $\phi\in L_{b}^{2}(\partial\tilde{D})$
    ]

    #me_idx = 28000627
    me_idx = 28000226 # TODO, (15117, 15116, 1)
    me_idx = 28000349 # Done, MEHorGroup, the children should be recursively processed
    me_idx = 28000982 # REV_REL_HOR, fixed
    me_idx = 28000627

    me_idx = 28001733 # X - \hat{X}
    me_idx = 28011948 # L_o = Y
    me_idx = 28000005 # very slow, need to check self loop
    me_idx = 28000051 # an empty group is created
    me_idx = 28000099 # accent overline z not working
    me_idx = 28000132 #
    me_idx = 28000166
    me_idx = 28000494
    me_idx = 28000023 # \partial b
    me_idx = 28000204 # f_{|b}, annotation error.
    me_idx = 28000548 # \phi . # TODO, design special processing to dot
    me_idx = 28001400 # \inV \cdot \Gamma . # TODO, design special processing to dot

    # round 7:23
    me_idx = 28012233  # suspect the under line is not processed correctly
    me_idx = 28003271  # suspect the ground truth is wrong, might be not consistency, the debug mode is good
    me_idx = 28001170 # g_* suspect that the * is used as binary  operator, I predict as sub, but gd as hor,
    me_idx = 28001493 # v^*_{-\lambda}, #TODO, both sup and sub not recognized

    # 9:37 of Dec. 18
    me_idx = 28006063 # 0.8
    me_idx = 28004328 # 0.8
    me_idx = 28003992 # 0.8
    me_idx = 28002883
    me_idx = 28001638
    me_idx = 28000341
    me_idx = 28000377 # 0.5 precision

    me_idx = 28007812 # 0.5 accuracy, with 7 elements
    me_idx = 28012673 # 0.2, k ( X_{ \\underline{a} }), NOTE, because that the under line touch the boundary of X
    me_idx = 28014860 # 0.3, [ \e_0 , \e_1 ], bug fixed?
    me_idx = 28008095 # 0.4, this is fucked up ..., G \times_H U, need to

    # done for now
    me_idx = 28001222 # 0.5, y_\lambda : Y_\lambda \mapsto C
    # y_\lambda ^ \colonY_\ lambda \rightarrowC, colon is not processed correctly?

    # TODO
    me_idx = 28011608 # mapsto, done
    me_idx = 28009100 # might be fixed

    me_idx = 28020271 # \Phi _ q, first the height of the Phi is too small, and also the subscript shifting too much, might lead to another limit
    me_idx = 28020194 # the size is not correct

    me_idx = 28013490 # the circle plus is acting as varying size symbol with binding variable. also the binding variables horizontal span could be over the op.
    me_idx = 28015942 # < \frac{p+1}{2}
    me_idx = 28004030 # \nu_0, very strange that something ending with the comma, how about just make it that the comma in the same level as the first char?

    me_idx = 28019292  # i = 1 ... n # Done
    me_idx = 28006702  # N_1 \times ... \times N_{2^j}
    me_idx = 28006702  # This is hard ... N_1 \times ... \times N_{2^j}

    # prior probability
    me_idx = 28005348  # plus not as the binary operator. TODO, need to think about also give this a prior probability
    me_idx = 28006786  # \nu_k * \mu^n, not sure about the ast, could be script or the binary operator.

    # configuration probability wrong ?
    me_idx = 28016418 # P_k = f_p g_p # TODO, out of expectation about the sizing. why not get the best one
    me_idx = 28020425  # L^{\mu_0} \times U^{\mu_0} # TODO, the size is not correct!!!
    me_idx = 28020188
    me_idx = 28000230 # \overline(\partial)_b f = 0 # TODO, out of clue what is here

    me_idx = 28000871 # test the vertical bar, how are they represented as latex value
    me_idx = 28007778 # test the double vertical bar , two pairs
    me_idx = 28020242 # might because of the accent to strict

    # the long me split error?
    me_idx = 28007043
    me_idx = 28017005
    me_idx = 28020515
    me_idx = 28006132
    #run_exp_by_me_idx_param(me_idx, debug=True)


if __name__ == "__main__":
    pass
    #test_parametric_model()

    #speed_test()

    #test_parametric_model()

    #re_run_by_sub_matching()
    # after delete the temporary result, run them again
    #batch_sequential()
    #batch_run_parallel()
