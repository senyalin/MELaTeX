"""
convert from Sciprt config, and list of me_group to construct a hor relationship only me_group
"""
from pdfxml.InftyCDB.macros import REL_SUB, REL_SUP
from pdfxml.me_layout.me_group.hor_me_group import MESubGroup, MESupGroup, MEHorGroup


def recursive_helper(head_idx, script_config, me_groups):
    """
    from the head_idx, first construct the hor list of idx
     then for each idx in the hor chain
     find the child, and from that child to recursive call
     after the children call return attach the children to the head

    :param head_idx:
    :param script_config:
    :type script_config: ScriptConfig
    :param me_groups:
    :return:
    """
    new_me_groups = []
    hor_chain = script_config.get_hor_chain(head_idx)
    for idx in hor_chain:
        # get the child of the current idx
        script_num = script_config.get_script_cid_rel_id_num(idx)
        assert script_num <= 1
        if script_num == 1:
            cid, rel_id = script_config.get_first_script_cid_rel_id(idx)
            script_me_group = recursive_helper(cid, script_config, me_groups)
            new_me_group = None
            if rel_id == REL_SUB:
                new_me_group = MESubGroup(me_groups[idx], script_me_group)
            elif rel_id == REL_SUP:
                new_me_group = MESupGroup(me_groups[idx], script_me_group)
            else:
                raise Exception("should not be so")
            new_me_groups.append(new_me_group)
        else:
            new_me_groups.append(me_groups[idx])
    return MEHorGroup(new_me_groups)


def script_config2me_group(script_config, me_groups):
    """
    need to recursively construct the me_group

    :param script_config:
    :type script_config: ScriptConfig
    :param me_groups:
    :type me_groups: list[MEGroup]
    :return:
    :rtype: MEHorGroup
    """
    return recursive_helper(0, script_config, me_groups)