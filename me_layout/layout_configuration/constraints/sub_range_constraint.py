"""
create new constraints for the sub range given the constraints for the whole range
"""
from pdfxml.InftyCDB.macros import CONS_HOR, CONS_EXIST_HOR, SCRIPT_LEVEL_SAME, SCRIPT_LEVEL_SAME_CENTER
from pdfxml.me_layout.layout_configuration.constraints.config_constraint import ConfigConstraint
from pdfxml.ds_range_util import in_range, range_intersect


def can_create_new_constraints(n, new_range, constraints):
    """
    check whether the new constraints could be create

    There are two types under consideration now:
        hard horizontal constrains
        range horizontal existence

    :param n:
    :param new_range: the boundary of the hole inclusive
    :param constraints: the original constraints
    :type constraints: list[ConfigConstraint]
    :return:
    """
    if constraints is None or len(constraints) == 0:
        # just empty, too
        return True

    for constraint in constraints:
        # ignore the constraints with root outside of the range
        if not in_range(constraint.id, new_range):
            continue
        for affect_info in constraint.affect_list:
            if affect_info['type'] == CONS_HOR:
                for j in range(affect_info['range'][0], affect_info['range'][1]+1):
                    if not in_range(j, new_range):
                        return False
            if affect_info['type'] == CONS_EXIST_HOR:
                found = False
                for j in range(affect_info['range'][0], affect_info['range'][1]+1):
                    if in_range(j, new_range):
                        found = True
                        break
                if not found:
                    return False
    return True


# TODO, this function is not implemented yet.???
# write done logic here
def create_new_constraints(n, new_range, constraints):
    """

    :param n: the number of element in the original list
    :param new_range: the range of the sub section in the original list
    :param constraints: the constraints on the original list
    :type constraints: list[ConfigConstraint]
    :return:
    """

    # TODO, logic not correct
    if not can_create_new_constraints(n, new_range, constraints):
        raise Exception("Should check this before call the current function")

    new_constraints = []
    for constraint in constraints:
        if not in_range(constraint.id, new_range):
            continue
        tmp_cc = ConfigConstraint(constraint.id - new_range[0], constraint.type)

        for affect_info in constraint.affect_list:
            if affect_info['type'] == CONS_HOR:
                tmp_cc.add_hor_constraint(
                    affect_info['range'][0] - new_range[0],
                    affect_info['range'][1] - new_range[0]
                )
            if affect_info['type'] == CONS_EXIST_HOR:
                ri = range_intersect(affect_info['range'], new_range)
                tmp_cc.add_hor_exist_constraint(
                    ri[0] - new_range[0], ri[1] - new_range[0])

            if affect_info['type'] == SCRIPT_LEVEL_SAME:
                if in_range(affect_info['id'], new_range):
                    tmp_cc.add_same_script_level_constraint(affect_info['id'] - new_range[0])

            if affect_info['type'] == SCRIPT_LEVEL_SAME_CENTER:
                if in_range(affect_info['id'], new_range):
                    tmp_cc.add_same_script_level_center_constraint(affect_info['id']-new_range[0])

        new_constraints.append(tmp_cc)
    return new_constraints
