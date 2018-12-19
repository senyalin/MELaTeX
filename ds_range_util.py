"""
The range is represented as inclusive
"""


############
# utility function to create constraints for the new range
############
def in_range(i, the_range):
    """

    :param i: the idx
    :param the_range: the inclusive range
    :return:
    """
    if i >= the_range[0] and i <= the_range[1]:
        return True
    return False


def range_intersect(r1, r2):
    """
    raise Exception if not
    """
    if (r1[1] < r2[0]) or (r1[0] > r2[1]):
        print r1, r2
        raise Exception("not overlapping")
    return max(r1[0], r2[0]), min(r1[1], r2[1])
