"""
Create constraints based on the content of operator, relation symbol, and punctuation
"""
from pdfxml.InftyCDB.macros import p_list
from pdfxml.InftyCDB.infty_cdb_util import get_glyph_type
from pdfxml.me_taxonomy.math_resources import is_unary_op
from pdfxml.me_layout.layout_configuration.constraints.config_constraint import ConfigConstraint

punct_name_list = [
    'comma', ',',
    "semicolon", ";", "\\semicolon",
    "colon", ":", "\\colon"]
punct_name_list.extend(p_list)
punct_name_list.extend(['\\'+p for p in p_list])


def create_op_rel_punct_constraints(char_name_list):
    """
    NOTE:
        bug list:
            * 28000023, \partial _b, but the current constraints function does not consider the subscript of the operators/relations
            *

    :param char_name_list: list of string of char name in inftycdb
    :type char_name_list: list[string]
    :return: list of constraints
    """
    constraint_list = []
    gt_list = [get_glyph_type(char_name) for char_name in char_name_list]

    for i, char_name in enumerate(char_name_list):
        gt = gt_list[i]
        if gt == 't':
            raise Exception("not handled yet {}".format(char_name))

        # create a new constraints
        if gt in ['o', 'r']:  # operator or relation
            # the i+1 element will match something before it
            # find the first op/rel before current
            tmp_constraint = None

            if char_name in ['-', '+', 'minus', 'plus', "perp", "\\perp", "\\times", "\\ast", "*"]: # they might be on the script only
                continue

            if is_unary_op(char_name):
                #if char_name == "-":
                # possibl negatition, only on the right part, not requiring the left part
                tmp_constraint = ConfigConstraint(i, gt)
                # boundary condition.
                if i + 1 < len(char_name_list):
                    tmp_constraint.add_hor_constraint(i+1, i+1)
                    constraint_list.append(tmp_constraint)
            else:
                tmp_constraint = ConfigConstraint(i, gt)
                if i + 1 < len(char_name_list):
                    tmp_constraint.add_hor_constraint(i + 1, i + 1)
                if i - 1 >= 0:
                    tmp_constraint.add_hor_exist_constraint(0, i-1)
                constraint_list.append(tmp_constraint)

        # comma, semicolon,
        # based on the logic below, the case should be good
        # because it check either direction
        if char_name in punct_name_list:
            # if char_name == 'comma' or char_name == ',':
            # there is a element before with the relation
            tmp_constraint = ConfigConstraint(i, gt)
            if i + 1 < len(char_name_list):
                tmp_constraint.add_hor_constraint(i + 1, i + 1)
            if i - 1 >= 0:
                tmp_constraint.add_hor_exist_constraint(0, i - 1)
            constraint_list.append(tmp_constraint)

    return constraint_list


def create_punct_constraints(char_name_list):
    """
    NOTE:
        bug list:
            * 28000023, \partial _b, but the current constraints function does not consider the subscript of the operators/relations
            *

    :param char_name_list: list of string of char name in inftycdb
    :type char_name_list: list[string]
    :return: list of constraints
    """
    constraint_list = []
    gt_list = [get_glyph_type(char_name) for char_name in char_name_list]

    for i, char_name in enumerate(char_name_list):
        gt = gt_list[i]
        if gt == 't':
            raise Exception("not handled yet {}".format(char_name))

        # comma, semicolon,
        # based on the logic below, the case should be good
        # because it check either direction
        if char_name in punct_name_list:
            # if char_name == 'comma' or char_name == ',':
            # there is a element before with the relation
            tmp_constraint = ConfigConstraint(i, gt)
            if i + 1 < len(char_name_list):
                tmp_constraint.add_hor_constraint(i + 1, i + 1)
            if i - 1 >= 0:
                tmp_constraint.add_hor_exist_constraint(0, i - 1)
            constraint_list.append(tmp_constraint)

    return constraint_list

