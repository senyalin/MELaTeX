"""
This module will enumerate all configuration given the list of no vertical relation samples.

TODO, write pseudo code for each of them

"""
import copy
import itertools

from pdfxml.InftyCDB.macros import REL_SUP, REL_SUB
from pdfxml.me_layout.layout_configuration.constraints.constraint_module import \
    constraint_sat
from pdfxml.me_layout.layout_configuration.constraints.sub_range_constraint import \
    can_create_new_constraints, create_new_constraints
from pdfxml.me_layout.layout_configuration.line_configuration_common import create_tmp_config, \
    create_h_elems_list, enumerate_one_element, full_enum_holes_configs, get_holes
from pdfxml.loggers import me_analysis_logger


def debug_hole_config(indent, holes_configs, full_expanded_holes_configs):
    """

    :param indent:
    :param holes_configs:
    :param full_expanded_holes_configs:
    :return:
    """
    me_analysis_logger.debug("{}holes configs".format(indent))
    me_analysis_logger.debug("{}{}".format(indent, holes_configs))
    me_analysis_logger.debug("{}each expand configs".format(indent))
    for full_expanded_holes_config in full_expanded_holes_configs:
        me_analysis_logger.debug("{}{}".format(indent, full_expanded_holes_config))
    me_analysis_logger.debug("{}end of each expaned config".format(indent))

def debug_merge_config(indent, org_config, new_config, hole_conf_pos_list):
    """

    :param indent:
    :param org_config:
    :param new_config:
    :param hole_conf_pos_list:
    :return:
    """
    me_analysis_logger.debug("==========")
    me_analysis_logger.debug("{}before merging{}".format(indent, org_config))
    me_analysis_logger.debug("{}config in sub range{}".format(indent, hole_conf_pos_list))
    me_analysis_logger.debug("{}a final config{}".format(indent, new_config))


# TODO, too long function, refactorize
# Still a bit long, after the first round of refactorization
def enumerate_configuration(n, constraints=[], indent='', debug=False):
    """

    assuming the first element is the biggest in layer

    :param n: the number of elements
    :param constraints:
        constraints are tuples (i, j, rel),
        where i and j are index, rel is the constrained relation
    :param indent: for debugging purpose to format the internal output
    :param debug:
    :return: list of ScriptConfig
    """
    if debug:
        me_analysis_logger.debug(
            "{0}\n{0}##############\n{0}call enumerate configuration {1}, {2}".format(
                indent, n, constraints)
        )

    if n == 1:
        return enumerate_one_element()

    res_config_list = []

    #h_elems_list = create_h_elems_list(n, indent, debug)  # enumerate the chain of horizontal elements
    h_elems_list = create_h_elems_list(n, constraints, indent, debug)
    for h_elems in h_elems_list:
        # step 1: check constrain satisfaction
        # step 2: create a base config, and get holes
        # step 3: for each hole, create temporary constrains, and recursively create ScriptConfig
        # step 4: in the product space, enumerate all possible combination of local config
        # step 5: merge the local config back to the global config

        if debug:
            me_analysis_logger.debug(
                "{}construction based on horizontal config {} with total len {}".format(
                    indent, h_elems, n)
            )

        # step 1
        if not constraint_sat(constraints, h_elems):  # check whether the constraints is satisfied here
            continue

        # step 2
        # create a temporary configuration here
        tmp_config = create_tmp_config(n, h_elems)
        if debug:
            me_analysis_logger.debug(
                "{}temporary config based on the horizontal relation{}".format(
                    indent, tmp_config)
            )

        holes = get_holes(n, h_elems)
        if debug:
            me_analysis_logger.debug(
                "{}holes{}".format(indent, holes)
            )

        # step 3,
        # TODO, NOTE, the logic below is not correct
        hole_violate_constraints = False
        for i, hole in enumerate(holes):
            if not can_create_new_constraints(n, hole, constraints):
                hole_violate_constraints = True
                break
        if hole_violate_constraints:
            # skip current h_elems due to hole not satisfying constraints.
            continue

        holes_config_pos_list = []
        for i in range(len(holes)):
            holes_config_pos_list.append([])

        for i, hole in enumerate(holes):
            if debug:
                me_analysis_logger.debug(
                    'create local config for hole {}'.format(i))
            local_n = hole[1] - hole[0] + 1
            # before the recursive call, the constraints will be reconstructed.
            if not can_create_new_constraints(n, hole, constraints):
                hole_violate_constraints = True
                break

            local_constraints = create_new_constraints(n, hole, constraints)
            # and for each hole, recursively call enumerate_configuration
            local_configs = enumerate_configuration(local_n, local_constraints, indent+'\t')

            if debug:
                me_analysis_logger.debug("{} {} {}".format(
                    local_n, len(local_configs), len(holes_config_pos_list[i])
                ))

            # the version with element level information is move to
            # line_configuration_with_element.py
            holes_config_pos_list[i].extend(
                itertools.product(local_configs, [REL_SUP, REL_SUB]))


            if debug:
                print indent, 'holes config', i
                for tmp_hc in holes_config_pos_list[i]:
                    print indent, indent, tmp_hc

        # step 4
        # Do an enumerate here,
        # we have the full combination of local config for each hole
        full_expanded_holes_config_list = full_enum_holes_configs(holes_config_pos_list)
        if debug:
            debug_hole_config(indent, holes_config_pos_list, full_expanded_holes_config_list)

        full_expanded_holes_config_list = full_enum_holes_configs(holes_config_pos_list)

        # step 5
        # add the local config to the global config
        for full_expanded_holes_config in full_expanded_holes_config_list:
            tmp_config_copy = copy.deepcopy(tmp_config)  # to avoid reference problem
            assert(len(full_expanded_holes_config) == len(holes))
            for i in range(len(holes)):
                # TODO, what is holes
                # full_expanded_holes_config[i] , pair of scriptconfig, SUP|SUB
                tmp_config_copy.update_config(holes[i], full_expanded_holes_config[i])
            res_config_list.append(tmp_config_copy)
            if debug:
                debug_merge_config(indent, tmp_config, tmp_config_copy, full_expanded_holes_config)

    return res_config_list
