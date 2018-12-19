"""
check level sameness
"""

from pdfxml.InftyCDB.macros import REL_UPPER, REL_UNDER, REL_H, REV_REL_SUB, REV_REL_SUP, REV_REL_H, REL_SUB, REL_SUP


def is_same_level(rel_list):
    """

    :param rel_list:
    :return:
    """
    upper_count = 0
    sup_count = 0
    sub_count = 0
    for rel in rel_list:
        if rel in [REL_H, REV_REL_H]:
            pass
        elif rel == REL_UPPER:
            upper_count += 1
        elif rel == REL_UNDER:
            upper_count -= 1
        elif rel == REL_SUB:
            sub_count += 1
        elif rel == REV_REL_SUB:
            sub_count -= 1
        elif rel == REL_SUP:
            sup_count += 1
        elif rel == REV_REL_SUP:
            sup_count -= 1
        else:
            raise Exception("unkonwn relation")
    return upper_count == 0 and sup_count == 0 and sub_count == 0