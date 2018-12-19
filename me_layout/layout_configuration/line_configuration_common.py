"""
The enumeration function used in both with element and without element
"""
import copy
import itertools

# TODO, one type of constraints, might need to move to me_layout_analysis
from pdfxml.InftyCDB.macros import SCRIPT_LEVEL_SAME, REL_H
from pdfxml.me_layout.layout_configuration.script_config import ScriptConfig


def enumerate_one_element():
    """
    return the possible script configuration when there is only one element

    :return:
    """
    sc = ScriptConfig()
    sc.add_triple(0, -1, None)
    return [sc]


def create_tmp_config(n, h_elems):
    """
    create a ScriptConfig only with the horizontal relations
    This scriptconfig will be expanded later to include the sup/sub elements

    :param n: TODO, not used
    :param h_elems:
    :rtype h_elems: list[int]
    :return:
    :rtype: ScriptConfig
    """
    """
    create a temporary configuration based on the current elements in the horizontal list
    each element, with the parent id and relation to the parent element
    """
    if h_elems[0] != 0:
        raise Exception("Should begin with 0 in my understanding, but as %s".format(str(h_elems)))
    tmp_sc = ScriptConfig()
    tmp_sc.add_triple(0, -1, None)
    for i in range(1, len(h_elems)):
        tmp_sc.add_triple(h_elems[i], h_elems[i-1], REL_H)
    return tmp_sc


def create_h_elems_list(n, constraints, indent="", debug=False):
    """
    must have the first element, my current assumption.

    :param n:
    :param constraints:
    :type constraints: list[ConfigConstraint]
    :param indent:
    :param debug:
    :return:
    """
    idx2hor_idx_set = {}
    for constraint in constraints:
        cid = constraint.id
        for affect in constraint.affect_list:
            if affect["type"] != SCRIPT_LEVEL_SAME:
                continue
            pid = affect["id"]
            if cid not in idx2hor_idx_set:
                idx2hor_idx_set[cid] = set()
            if pid not in idx2hor_idx_set:
                idx2hor_idx_set[pid] = set()
            idx2hor_idx_set[cid].add(pid)
            idx2hor_idx_set[pid].add(cid)

    cur_list = [0]
    res_list = []
    if debug:
        print constraints
    recursive_create_h_elems_list(
        n,
        1, # next cand_idx
        cur_list,
        set(),
        set(), idx2hor_idx_set, res_list)

    return res_list


def full_enum_holes_configs(holes_sc_list):
    """
    create product space of sc list of all the holes
    The input is list( list(holes_config, pos) )
    the internal list is all possible for a hole

    :param holes_sc_list: list of possible script config for each hole
        holes_configs is list of list
        holes_configs[i] is the list of configs for one hole
    :return:
    """
    return itertools.product(*holes_sc_list)


def get_holes(n, h_elems):
    """
    return the range holes based on the elements in horizontal now
    each hole is represented by the start position and end position included the boundary

    :param n: the total number of elements
    :param h_elems: the chain of horizontal relation at the top layer
    :return:
        each hole is a pair that indicates inclusive range
    """
    res = []
    h_elems.sort()
    i = 0
    # i would be the first element in the h_elems
    while True:
        # get the first valid position not in h_elems
        s = i
        while s < n and s in h_elems:
            s += 1
        if s >= n:
            break

        # start from this position, get the valid ending position
        e = s+1
        while e < n and e not in h_elems:
            e += 1
        if e < n:
            res.append([s, e-1])
        else:
            res.append([s, n-1])
        i = e+1  # update the index

    return res


def recursive_create_h_elems_list(n, next_cand_idx,
                                  cur_list,
                                  must_in_set,
                                  must_not_in_set,
                                  idx2hor_idx_set,
                                  res_list):
    """

    :param n:
    :param next_cand_idx:
    :param cur_list:
    :param must_in_set:
    :type must_in_set: set
    :param must_not_in_set:
    :param idx2hor_idx_set:
    :param res_list:
    :return:
    """
    # logical conflict
    if must_in_set.intersection(must_not_in_set):
        return

    # stop condition
    if next_cand_idx >= n:
        res_list.append(copy.copy(cur_list))
        return

    if next_cand_idx in must_in_set:
        # must add it
        cur_list.append(next_cand_idx)
        recursive_create_h_elems_list(
            n,
            next_cand_idx+1,
            cur_list,
            must_in_set,
            must_not_in_set,
            idx2hor_idx_set,
            res_list
        )
        del cur_list[-1]
    elif next_cand_idx in must_not_in_set:
        # not adding the current one
        recursive_create_h_elems_list(
            n,
            next_cand_idx + 1,
            cur_list,
            must_in_set,
            must_not_in_set,
            idx2hor_idx_set,
            res_list
        )
    else:
        # either add or not
        # first not add it, but need to update the must_not_in_set
        new_must_not_in_set = must_not_in_set
        if next_cand_idx in idx2hor_idx_set:
            new_must_not_in_set = copy.copy(must_not_in_set)
            new_must_not_in_set.update(idx2hor_idx_set[next_cand_idx])
        recursive_create_h_elems_list(
            n,
            next_cand_idx + 1,
            cur_list,
            must_in_set,
            new_must_not_in_set,
            idx2hor_idx_set,
            res_list
        )

        # second add the next_cand_idx, need to update the must_in_set
        new_must_in_set = must_in_set
        if next_cand_idx in idx2hor_idx_set:
            new_must_in_set = copy.copy(must_in_set)
            new_must_in_set.update(idx2hor_idx_set[next_cand_idx])
        cur_list.append(next_cand_idx)
        recursive_create_h_elems_list(
            n,
            next_cand_idx + 1,
            cur_list,
            new_must_in_set,
            must_not_in_set,
            idx2hor_idx_set,
            res_list
        )
        del cur_list[-1]