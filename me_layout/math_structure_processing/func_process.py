"""
func process means group the chars for function name
"""
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.internal_me_group import MEHSSGroup, MEHorSupOrSubGroup
from pdfxml.me_layout.me_group.hor_me_group import MESubGroup, MESupGroup, MEHorGroup
from pdfxml.me_layout.me_group.vertical_me_group import MESupSubGroup, MEBindVarGroup, MEUpperGroup, MEUnderGroup, \
    MEFractionGroup, \
    MEAccentGroup, MEUpperUnderGroup, GridGroup
from pdfxml.me_layout.me_group.enclosed_me_group import MERadicalGroup, MEFenceGroup
from pdfxml.me_layout.pss_exp.pss_exception import NoneMEGroupException
from pdfxml.me_taxonomy.math_resources import func_name_list, max_func_name_len, words_list


def recursive_organize_func_in_hs_group(mg):
    """
    recursively group the function names which is split into multiple MESymbolGroup

    :param mg:
    :return:
    """
    if isinstance(mg, MESymbolGroup):
        return mg
    elif isinstance(mg, MEBindVarGroup):
        mg.up_me_group = recursive_organize_func_in_hs_group(mg.up_me_group)
        mg.down_me_group = recursive_organize_func_in_hs_group(mg.down_me_group)
        return mg
    elif isinstance(mg, MEFractionGroup):
        mg.up_me_group = recursive_organize_func_in_hs_group(mg.up_me_group)
        mg.down_me_group = recursive_organize_func_in_hs_group(mg.down_me_group)
        return mg
    elif isinstance(mg, MEAccentGroup):
        mg.me_group = recursive_organize_func_in_hs_group(mg.me_group)
        return mg
    elif isinstance(mg, MEHorSupOrSubGroup):
        return organize_func_in_hs_group(mg)
    elif isinstance(mg, MEFenceGroup):
        mg.hs_group = recursive_organize_func_in_hs_group(mg.hs_group)
        return mg
    elif isinstance(mg, MESupSubGroup):
        mg.base_me_group = recursive_organize_func_in_hs_group(mg.base_me_group)
        mg.sup_me_group = recursive_organize_func_in_hs_group(mg.sup_me_group)
        mg.sub_me_group = recursive_organize_func_in_hs_group(mg.sub_me_group)
        return mg
    elif isinstance(mg, MESupGroup):
        mg.base_me_group = recursive_organize_func_in_hs_group(mg.base_me_group)
        mg.sup_me_group = recursive_organize_func_in_hs_group(mg.sup_me_group)
        return mg
    elif isinstance(mg, MESubGroup):
        mg.base_me_group = recursive_organize_func_in_hs_group(mg.base_me_group)
        mg.sub_me_group = recursive_organize_func_in_hs_group(mg.sub_me_group)
        return mg

    elif isinstance(mg, MEHSSGroup):
        # TODO, NOTE, there might introduce some error here.
        return organize_func_in_hs_group(mg)
        #raise Exception("Not know what to do yet")
    elif isinstance(mg, MEHorGroup):
        # if I try to organize it a gain, with the possibility of infinite processing
        # some special checking is done to make sure of no infinite recursive
        mg = organize_func_in_hs_group(mg)
        return mg # Hor group is already done
    elif isinstance(mg, MERadicalGroup):
        mg.me_group = recursive_organize_func_in_hs_group(mg.me_group)
        return mg
    elif mg is None:
        raise NoneMEGroupException()
    elif isinstance(mg, EmptyGroup):
        return mg
    elif isinstance(mg, MEUpperGroup):
        mg.base_me_group = recursive_organize_func_in_hs_group(mg.base_me_group)
        mg.upper_me_group = recursive_organize_func_in_hs_group(mg.upper_me_group)
        return mg
    elif isinstance(mg, MEUnderGroup):
        mg.base_me_group = recursive_organize_func_in_hs_group(mg.base_me_group)
        mg.under_me_group = recursive_organize_func_in_hs_group(mg.under_me_group)
        return mg
    elif isinstance(mg, MEUpperUnderGroup):
        mg.base_me_group = recursive_organize_func_in_hs_group(mg.base_me_group)
        mg.under_me_group = recursive_organize_func_in_hs_group(mg.under_me_group)
        mg.upper_me_group = recursive_organize_func_in_hs_group(mg.upper_me_group)
        return mg
    elif isinstance(mg, GridGroup):
        for r in range(len(mg.mg_mat)):
            for c in range(len(mg.mg_mat[r])):
                mg.mg_mat[r][c] = recursive_organize_func_in_hs_group(mg.mg_mat[r][c])
        return mg
    else:
        print "recursive_organize_fence_in_hs_group", type(mg)
        raise Exception("TODO")


def organize_func_in_hs_group(mg):
    """
    look for index and create a horizontal group
    :param mg:
    :return: update the me_groups of mg, and return it
    """

    # first recursive process each one
    #"""
    # NOTE, comment out for debugging the function matching
    new_me_groups = []
    for me_group in mg.me_groups:
        new_me_groups.append(
            recursive_organize_func_in_hs_group(me_group)
        )
    mg.me_groups = new_me_groups
    #"""
    if len(new_me_groups) == 13:
        # for debug
        pass
    # by the end, process the current layer
    # look for consecutive MESymbolGroup and test whether the combination is in the func_name_list
    while True:
        # iteratively find and merge them
        start_i = 0 # the start index
        end_i = -1
        found_func = False
        func_under_group = None
        me_groups = mg.me_groups
        while start_i < len(me_groups):
            end_i_list = []

            tmp_str = ""
            for j in range(max_func_name_len):
                if start_i + j >= len(me_groups):
                    break
                cur_me_group = me_groups[start_i+j]

                is_symbol_group = isinstance(cur_me_group, MESymbolGroup)
                is_under_group = (isinstance(cur_me_group, MEUnderGroup) and isinstance(cur_me_group.base_me_group, MESymbolGroup))
                if not (is_symbol_group or is_under_group):
                    break

                cur_me_group_str = ""
                if is_symbol_group:
                    cur_me_group_str = str(cur_me_group)
                elif is_under_group:
                    cur_me_group_str = str(cur_me_group.base_me_group)
                    func_under_group = cur_me_group.under_me_group
                else:
                    raise Exception("unexpected type")

                if not len(cur_me_group_str) == 1:
                    break

                tmp_str += cur_me_group_str
                if tmp_str in func_name_list or tmp_str in words_list:
                    found_func = True
                    end_i = start_i+j
                    #break
                    end_i_list.append(end_i)


            # make sure not the only thing in the MEHorGroup, to avoid infinite recursive
            if isinstance(mg, MEHorGroup) and start_i == 0 and end_i+1 == len(me_groups):
                found_func = False

            if found_func:
                end_i = end_i_list[-1]  # pick the last one that could make an function

                # process the me_groups and assign the new one to mg
                # start_i and end_i inclusive
                func_symbol_groups = []
                for k in range(start_i, end_i + 1):
                    if isinstance(mg.me_groups[k], MESymbolGroup):
                        func_symbol_groups.append(mg.me_groups[k])
                    elif isinstance(mg.me_groups[k], MEUnderGroup):
                        func_symbol_groups.append(mg.me_groups[k].base_me_group)
                    else:
                        raise Exception("unknown situation")

                func_group = MEHorGroup(func_symbol_groups)
                if func_under_group:
                    # if originally have under.
                    func_group = MEUnderGroup(func_group, func_under_group)

                new_me_groups = [mg.me_groups[i] for i in range(start_i)]
                new_me_groups.append(func_group)
                new_me_groups.extend(mg.me_groups[end_i+1:])
                mg.me_groups = new_me_groups

                break
            start_i += 1
        if not found_func:
            break
    return mg


def is_func_hgroup(hgroup):
    """

    :param hgroup:
    :return:
    """
    if isinstance(hgroup, MEHorGroup):
        s = ""
        for mg in hgroup.me_groups:
            if not isinstance(mg, MESymbolGroup):
                return False
            s += mg.me_symbol.latex_val
        if s in func_name_list:
            return True
    return False