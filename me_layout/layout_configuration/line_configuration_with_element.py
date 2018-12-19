"""
Compared with the line_configuration.py,
The enumeration process in this file also based on the element information
More specific, the normalized bounding box is used to reduce the possible configuration at each children.
"""

import copy
import itertools
import pdfxml.me_layout.me_layout_config as me_layout_config
from pdfxml.InftyCDB.macros import REL_SUP, REL_SUB
from pdfxml.me_layout.layout_configuration.constraints.constraint_module import constraint_sat
from pdfxml.me_layout.layout_configuration.constraints.sub_range_constraint import create_new_constraints, \
    can_create_new_constraints
from pdfxml.me_layout.layout_configuration.line_configuration_common import enumerate_one_element, \
    create_h_elems_list, full_enum_holes_configs, create_tmp_config, get_holes


def enumerate_configuration_with_elements(elem_list, constraints=[]):
    """
    The only difference so far is that when the local configuration
     attach to parent, should decide as SUP or SUB if possible.

    :param elem_list:
        should be ME Groups, need to have the get center function
    :param constraints:
    :return:
    """
    n = len(elem_list)
    if n == 1:
        return enumerate_one_element()

    res_config_list = []

    h_elems_list = create_h_elems_list(n, constraints)
    for h_elems in h_elems_list:
        # step 1: check constrain satisfaction
        # step 2: create a base config, and get holes
        # step 3: for each hole, create temporary constrains, and recursively create ScriptConfig
        # step 4: in the product space, enumerate all possible combination of local config
        # step 5: merge the local config back to the global config

        # step 1
        if not constraint_sat(constraints, h_elems):  # check whether the constraints is satisfied here
            continue

        # step 2
        # create a temporary configuration here based on the chain of horizontal elements
        tmp_config = create_tmp_config(n, h_elems)

        holes = get_holes(n, h_elems)

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
            # 'create local config for hole {}'.format(i)

            # before the recursive call, the constraints will be reconstructed.
            if not can_create_new_constraints(n, hole, constraints):
                hole_violate_constraints = True
                break

            # create the local configurations for a hole
            local_constraints = create_new_constraints(n, hole, constraints)
            # and for each hole, recursively call enumerate_configuration
            local_elems = [elem_list[ei] for ei in range(hole[0], hole[1]+1)]
            local_configs = enumerate_configuration_with_elements(local_elems, local_constraints)

            # TODO, one way to reduce the possibility of enumeration is to compare the center
            # if the center is above it, very little opportunity to be subscript
            # if the center is below it, unlikely to be superscript

            #from me_layout_config.prediction_options import OPTION_A_4_LOCAL_CONFIG_BY_CENTER
            if not me_layout_config.OPTION_A_4_LOCAL_CONFIG_BY_CENTER:
                # if not set true, then add both SUP and SUB without concerning the relative position
                holes_config_pos_list[i].extend(
                    itertools.product(local_configs, [REL_SUP, REL_SUB]) )
            else:
                # for each local configs, get the first element with normalizable height
                # if the element to be attached with normalizable height
                # the first normalize the bounding box of the two and then compare
                # otherwise if not feasible, still add both SUP and SUB

                # the index of the parent element
                pid = hole[0]-1
                # hole[0] is the beginning of the hole
                # just call get center
                # might not need it to be normalizable. parenthesis are y-symmetric

                # the first element of the children to find the center
                cid = hole[0]

                # need to have the get center function for each element
                p_center = elem_list[pid].get_center()[1] # 1 means the second (vertical) dimension
                c_center = elem_list[cid].get_center()[1]
                if c_center < p_center:
                    holes_config_pos_list[i].extend(
                        itertools.product(local_configs, [REL_SUB]))
                else:
                    holes_config_pos_list[i].extend(
                        itertools.product(local_configs, [REL_SUP]))

            # finish enumeration of the hole_config_pos_list

        # step 4
        # Do an enumerate here,
        # we have the full combination of local config for each hole
        full_expanded_holes_config_list = full_enum_holes_configs(holes_config_pos_list)

        # step 5
        # add the local config to the global config
        for full_expanded_holes_config in full_expanded_holes_config_list:
            # TODO, NOTE, here might be pretty costly,
            # is it possible to use dfs without enumerating all configuration
            # and find the best one?
            tmp_config_copy = copy.deepcopy(tmp_config)  # to avoid reference problem
            assert(len(full_expanded_holes_config) == len(holes))
            for i in range(len(holes)):
                # full_expanded_holes_config[i] , pair of scriptconfig, SUP|SUB
                # attach the configuration of one local hole to the global
                # the position of the hole is as "holes[i]",
                tmp_config_copy.update_config(holes[i], full_expanded_holes_config[i])
            res_config_list.append(tmp_config_copy)

    return res_config_list

