"""
no matter what dataset is used,
this exp common is the common function used by them
"""

import copy
import numpy as np
import pdfxml.me_layout.me_layout_config as me_layout_config
from pdfxml.pdf_util.bbox import BBox
from pdfxml.me_layout.layout_configuration.line_configuration import enumerate_configuration
from pdfxml.me_layout.layout_prediction.pos_features import height_ratio_AB, normalized_ycenter_diff_AB
from pdfxml.me_layout.layout_prediction.simulation_based_dist import get_hr_dist, get_nycd_dist

# TODO, to be abandoend
hr_pdf_cache = {} # a cache from the rel_list to pdf
nycd_pdf_cache = {}

hr_dist_cache = {} # a cache from the rel_list to pdf
nycd_dist_cache = {}


def get_dist(rel_list, fea):
    """
    get a distribution object

    :param rel_list:
    :param fea:
    :return:
    """
    rel_list_str = "_".join([str(rel) for rel in rel_list])  # key
    if fea == "hr":
        if rel_list_str in hr_pdf_cache:
            return hr_pdf_cache[rel_list_str]

        hr_dist = get_hr_dist(rel_list)
        hr_dist_cache[rel_list_str] = hr_dist
        return hr_dist_cache[rel_list_str]

    elif fea == "nycd":
        if nycd_pdf_cache.has_key(rel_list_str):
            return nycd_pdf_cache[rel_list_str]

        nycd_dist = get_nycd_dist(rel_list)
        nycd_pdf_cache[rel_list_str] = nycd_dist
        return nycd_pdf_cache[rel_list_str]

    else:
        raise Exception("unknow feature")


def predict_with_elems_constraints(element_list, constraints=None, debug=False):
    """
    each elem is describe the value, and the bounding box
    It is assumed that the element list are ordered from left to right
    There is no vertical overlapping

    :param element_list: list of me groups
    :type element_list: list[MEGroup]
    :param constraints:
        constraints is passed to this function,
         not generated within
    :return:
    :rtype: ScriptConfig
    """
    # TODO, The interface might need to be more flexible to consider the ME group
    # TODO, what are the information required to create such constraints?

    # enumerate all possible configuration
    config_list = enumerate_configuration(len(element_list), constraints)
    if debug:
        print 'there is a total of %d possible configs'%(len(config_list))
    if len(config_list) == 0:
        raise Exception("no possible configurations")

    # adjust the bbox here
    adjusted_bbox_list = [element.get_adjusted_bbox() for element in element_list]

    # for each configuration, generate the paired relation for all pairs
    # TODO, later
    # constraint_id_list = [c['id'] for c in constraints]

    # remove the common among different configurations
    config2org_pair_rel_set = {}
    for config in config_list: # ScriptConfig type
        pair_rel_set = set(config.get_pair_rel_list(me_groups=element_list))
        config2org_pair_rel_set[config] = pair_rel_set
    if debug:
        for config, org_pair_rel_set in config2org_pair_rel_set.items():
            print "##"
            print config
            print org_pair_rel_set


    if me_layout_config.OPTION_Z1_REMOVE_COMMON_CPRC:
        # get the common among all
        # print some information here
        common_pair_rel_set = copy.copy(config2org_pair_rel_set.values()[0])
        for org_pair_rel_set in config2org_pair_rel_set.values():
            ":type common_pair_rel_set: set"
            common_pair_rel_set.intersection_update(org_pair_rel_set)
        if debug:
            print "len of the common set part {}".format(len(common_pair_rel_set))
        config2reduced_pair_rel_set = {}
        for config, org_pair_rel_set in config2org_pair_rel_set.items():
            config2reduced_pair_rel_set[config] = org_pair_rel_set.difference(common_pair_rel_set)
    else:
        config2reduced_pair_rel_set = config2org_pair_rel_set

    log_sum_list = []
    for config in config_list: # ScriptConfig type
        #pair_rel_set = config.get_pair_rel_list()
        pair_rel_set = config2reduced_pair_rel_set[config]
        log_sum = 0.
        for pair_rel in pair_rel_set:
            # for each pair, evaluate the probability and sum of log
            i, j, rel_list = pair_rel

            #if i in constraint_id_list or j in constraint_id_list:
            #    # pass this
            #    continue
            if isinstance(adjusted_bbox_list[i], BBox):
                hr = height_ratio_AB(
                    adjusted_bbox_list[i].quadruple,
                    adjusted_bbox_list[j].quadruple)
                nycd = normalized_ycenter_diff_AB(
                    adjusted_bbox_list[i].quadruple,
                    adjusted_bbox_list[j].quadruple)
            else:
                hr = height_ratio_AB(
                    adjusted_bbox_list[i], adjusted_bbox_list[j])
                nycd = normalized_ycenter_diff_AB(
                    adjusted_bbox_list[i], adjusted_bbox_list[j])

            # might be slow here possible because of load the pdf each time

            hr_dist = get_dist(rel_list, "hr")
            nycd_dist = get_dist(rel_list, "nycd")

            log_sum += np.log(hr_dist.pdf(hr))
            log_sum += np.log(nycd_dist.pdf(nycd))
        log_sum_list.append(log_sum)
        if debug:
            print config, log_sum, len(pair_rel_set)
    # sort and get the best config
    max_idx = np.argmax(log_sum_list)
    return config_list[max_idx]
