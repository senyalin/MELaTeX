"""
This file includes the following important parts:
 1. construct the constraints based on the list of char names
 2. constrains satisfaction checking
 3. sub constrains creation for the holes

Some confirmed not consistent constraitns:
 * big op, right might be sub, left might be sub/sup of previous things
"""
from pdfxml.me_layout.me_group.me_group import MESymbol
from pdfxml.me_layout.char_adjust_bbox_core import can_cal_center, could_estimate_height
from pdfxml.me_layout.layout_configuration.constraints.config_constraint import ConfigConstraint
from pdfxml.InftyCDB.macros import CONS_EXIST_HOR, CONS_HOR, SCRIPT_LEVEL_SAME, SCRIPT_LEVEL_SAME_CENTER
from pdfxml.me_layout.layout_configuration.constraints.op_rel_punct_constraint import create_op_rel_punct_constraints, \
    create_punct_constraints


#############
# create new constraints
#############
def create_center_line_constraints(mg_list):
    """
    based on the char with adjustable height
    check against chars with adjustable height and centered glyph

    :param mg_list:
    :return:
    """
    import pdfxml.me_layout.me_layout_config as me_layout_config
    thres = me_layout_config.center_band_threshold

    cc_list = []
    # the math symbols with center recoverable
    center_ms_list = [mg.get_baseline_symbol() for mg in mg_list]
    # The main symbol might be None, for the general under/upper, because not knowing the arrange
    # TODO, still might reover the main through the center line analysis
    for ms in center_ms_list:
        if not isinstance(ms, MESymbol):
            pass

    for i, mg in enumerate(mg_list):
        main_symbol = center_ms_list[i]
        if main_symbol is None or not could_estimate_height(main_symbol):
            continue
        #if not is_adjustable(main_symbol):
        #    continue
        # look for the mg on the right that should be on the same center line
        v_center = main_symbol.get_v_center()
        v_height = main_symbol.get_adjust_height()
        v_lb = v_center - v_height*thres
        v_ub = v_center + v_height*thres
        for j in range(len(mg_list)):
            if i == j:
                continue
            tmp_main_symbol = center_ms_list[j]
            if tmp_main_symbol is None:
                continue

            if could_estimate_height(tmp_main_symbol):
                # do a double direction check
                tmp_v_center = tmp_main_symbol.get_v_center()
                tmp_v_height = tmp_main_symbol.get_adjusted_bbox().height()
                cond1 = v_lb <= tmp_v_center <= v_ub
                cond2 = tmp_v_center-tmp_v_height*thres <= v_center <= tmp_v_center+tmp_v_height*thres
                if cond1 and cond2:
                    cc = ConfigConstraint(i, 'center')  # the gt is only a descript or the glyph type
                    # cc.add_same_script_level_constraint(j)
                    cc.add_same_script_level_center_constraint(j)
                    cc_list.append(cc)

            elif can_cal_center(tmp_main_symbol):
                tmp_v_center = tmp_main_symbol.get_v_center()
                if v_lb <= tmp_v_center <= v_ub:
                    cc = ConfigConstraint(i, 'center')  # the gt is only a descript or the glyph type
                    #cc.add_same_script_level_constraint(j)
                    cc.add_same_script_level_center_constraint(j)
                    cc_list.append(cc)

    return cc_list


def create_constraints_for_mg_list(me_group_list):
    """
    create the constraints from list of ME groups
    1. the dominance based
    2. the center line based analysis

    :param me_group_list:
    :return:
    """
    import pdfxml.me_layout.me_layout_config as me_layout_config
    mg_str_list = [str(mg) for mg in me_group_list]
    constraint_list = []

    if me_layout_config.enable_op_constraint:
        constraint_list.extend(create_op_rel_punct_constraints(mg_str_list))

    constraint_list.extend(create_punct_constraints(mg_str_list))

    constraint_list.extend(create_center_line_constraints(me_group_list))
    return constraint_list


#####
# the constraints satisfaction checking
#####
def constraint_sat(constraints, h_elems, debug=False):
    """
    test whether the partially given constraints could be satisified

    NOTE,
     - only the horizontal relation are passed here
     - only check current layer

    TODO, what are the two parameters mentioned above?

    :param constraints:
        constraints are list of tuples (i, j, rel), currently only HOR relation for now
        also include the script_level_constraints

        tmp_constraint = {
            'id':i,
            'type': gt,
            'affect':[
                {'range':[i+1, i+1], 'type':CONS_HOR},
                {'range':[b, i-1], 'type':CONS_EXIST_HOR},
            ]
        }
    :type constraints: list[ConfigConstraint]
    :param h_elems:
    :return:
    """
    #
    if debug:
        print 'checking constraint sat on ', h_elems
    if not constraints:
        return True

    # Script level checking
    for constraint in constraints:
        i = constraint.id
        for affect in constraint.affect_list:
            if affect["type"] == SCRIPT_LEVEL_SAME:
                j = affect["id"]
                if j not in h_elems and i in h_elems:
                    return False
                if j in h_elems and j not in h_elems:
                    return False
            if affect['type'] == SCRIPT_LEVEL_SAME_CENTER:
                # either both in the range, or both not in the range.
                j = affect['id']
                if i in h_elems and j not in h_elems:
                    return False
                if i not in h_elems and j in h_elems:
                    return False

    # CONS_HOR CONS_EXIST_HOR
    for constraint in constraints:
        i = constraint.id
        if i not in h_elems:
            # the current enumeration of the horizontal chain is not including i
            continue
        for affect in constraint.affect_list:
            if affect['type'] == CONS_HOR:
                # inclusive range
                for j in range(affect['range'][0], affect['range'][1]+1):
                    if j not in h_elems:
                        if debug:
                            print h_elems, "violation of the hard constrain not satisfied"
                        return False
            elif affect['type'] == CONS_EXIST_HOR:
                found = False
                for j in range(affect['range'][0], affect['range'][1]+1):
                    if j in h_elems:
                        found = True
                if not found:
                    if debug:
                        print h_elems, "violation of the lose constrain not satisfied"
                    return False

    # both Script_level, hor, hor_exist passed
    return True


def constraint_sat_for_config_for_must_hor(sc, constraint_list):
    """

    :param sc: ScriptConfig
    :type: ScriptConfig
    :param constraints:
    :return:
    """
    for constraint in constraint_list:
        id1 = constraint.id
        for affect_dict in constraint.affect_list:
            if 'id' in affect_dict:
                id2 = affect_dict['id']
                affect_type = affect_dict['type']
                if affect_type == SCRIPT_LEVEL_SAME or affect_type == CONS_HOR:
                    if not sc.same_level(id1, id2):
                        return False
            if 'range' in affect_dict:
                affect_type = affect_dict['type']
                if affect_type == SCRIPT_LEVEL_SAME or affect_type == CONS_HOR:
                    for id2 in range(affect_dict['range'][0], affect_dict['range'][1]):
                        if not sc.same_level(id1, id2):
                            return False

    return True
