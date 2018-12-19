"""
Input: after the hat, bind_var processing, UnorganizedGroupPath
Output:
* might still be an UGP, but the some MEGroup and MEPath are grouped together into MESqrtGroup
* Might just return a MESqrtGroup
* No matter which condition, still MEGroup

"""

from pdfxml.pdf_util.bbox import merge_bbox
from pdfxml.me_layout.me_group.atomic_me_group import MESymbolGroup
from pdfxml.me_layout.me_group.enclosed_me_group import MERadicalGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath
from pdfxml.me_layout.pss_exp.pss_exception import SqrtProcessingException

#######
# group construction
#######

def organize_sqrt_in_ugp(ugp):
    while True:

        smallest_sqrt_bound = get_smallest_sqrt_bound_from_ugp(ugp)
        if not smallest_sqrt_bound:
            break
        # create a new MESqrtGroup
        # create a new UnorganizedGroupPath
        keep_me_groups = []
        keep_me_paths = []
        within_sqrt_me_groups = []
        within_sqrt_me_paths = []

        me_sqrt_group = MERadicalGroup(smallest_sqrt_bound[0], smallest_sqrt_bound[1], [])

        for me_group in ugp.me_groups:

            if isinstance(me_group, MESymbolGroup):
                if me_group.me_symbol.get_tight_bbox().overlap(smallest_sqrt_bound[0].get_tight_bbox()):
                    common_bbox = me_group.me_symbol.get_tight_bbox().intersect(
                        smallest_sqrt_bound[0].get_tight_bbox())
                    if common_bbox.area() / smallest_sqrt_bound[0].get_tight_bbox().area() > 0.8:
                        continue

            if me_sqrt_group.get_tight_bbox().contains(me_group.get_tight_bbox().center()):
                # if bbox_within(me_group.get_tight_bbox(), me_sqrt_group.get_tight_bbox()):
                within_sqrt_me_groups.append(me_group)
            else:
                keep_me_groups.append(me_group)

        for me_path in ugp.me_paths:

            if me_path == smallest_sqrt_bound[1]:
                continue
            if me_sqrt_group.get_tight_bbox().contains(me_path.get_tight_bbox().center()):
                # if bbox_within(me_path.get_tight_bbox(), me_sqrt_group.get_tight_bbox()):
                within_sqrt_me_paths.append(me_path)
            else:
                keep_me_paths.append(me_path)

        # the ME Sqrt group
        sqrt_within_me_group = UnorganizedGroupPath(
            within_sqrt_me_groups,
            within_sqrt_me_paths)
        me_sqrt_group.set_me_group(sqrt_within_me_group)

        # update the Original unorganized group
        keep_me_groups.append(me_sqrt_group)
        ugp.set_me_groups(keep_me_groups)
        ugp.set_me_paths(keep_me_paths)


def get_sqrt_bounds_from_ugp(ugp):
    """
    sqrt_bound is defined as the part of Sqrt symbol and the associated Path
    This function will get all such pairs,
    only try to find the symbol among ugp.me_groups, not recursively do it (assuming sub_group are done)

    :param ugp: UnorganizedGroupPath
    :return:
    """
    sqrt_bounds = []
    for me_group in ugp.me_groups:
        if not isinstance(me_group, MESymbolGroup) or not me_group.is_radical():
            continue
        # try to find the matching path
        sqrt_path = get_path_for_sqrt_symbol(me_group.me_symbol, ugp.me_paths)
        #assert(sqrt_path != None) # should always have one matching path
        if sqrt_path == None:
            raise SqrtProcessingException("sqrt path not found")
        sqrt_bound = (me_group.me_symbol, sqrt_path)
        sqrt_bounds.append(sqrt_bound)
    return sqrt_bounds


def get_smallest_sqrt_bound_from_ugp(ugp):
    """

    :param ugp: Unorganized Group Path
    :return:
        a sqrt bound is a pair of (sqrt symbol, sqrt path)
        the smallest is the one such that contain no other isolated sqrt symbol
        None if no such sqrt bound
    """
    # first get all pairs of (sqrt symbol, sqrt path)
    sqrt_bounds = get_sqrt_bounds_from_ugp(ugp)

    # find the first sqrt_bound that does not contain other sqrt_bound
    # to check the contain relation, first get the tight bounding box of all
    bbox_list = []
    for sqrt_bound in sqrt_bounds:
        bbox_list.append(
            merge_bbox(
                sqrt_bound[0].get_tight_bbox(),
                sqrt_bound[1].get_tight_bbox()
            ))

    for i, sqrt_bound in enumerate(sqrt_bounds):
        no_contain_other = True
        for j in range(len(sqrt_bounds)):
            if i == j:
                continue
            if bbox_list[i].contains(bbox_list[j].center()):
                # if bbox_within(bbox_list[j], bbox_list[i]):
                no_contain_other = False
                break
        if no_contain_other:
            return sqrt_bound
    return None


def get_path_for_sqrt_symbol(sqrt_symbol, paths):
    assert(sqrt_symbol.is_radical())
    for path in paths:
        if sqrt_symbol_path_match(sqrt_symbol, path):
            return path
    return None


def sqrt_symbol_path_match(sqrt_symbol, path):
    """

    :param sqrt_symbol: assuming it is sqrt symbol
    :param path:
    :return:
    """
    assert(sqrt_symbol.is_radical())
    symbol_bbox = sqrt_symbol.get_tight_bbox()
    path_bbox = path.get_tight_bbox()

    if abs(symbol_bbox.right() - path_bbox.left()) > 2:
        return False
    # hard coded rules here
    if path_bbox.top() > symbol_bbox.bottom() and path_bbox.top() < symbol_bbox.top()+2:
        return True
    return False


