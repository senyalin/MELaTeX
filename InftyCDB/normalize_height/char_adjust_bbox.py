"""
Infty:
code2name, name2code

gt is short for glyph type

Given a LTChar, font
based on the glyph name, ascii/unicode value,
try to match the name2code
Find the matching code and adjust parameters,

adjust_bbox_h_gt and adjust_bbox_h_gt_name are the two core functions.
"""
import copy
import numpy as np
from pdfxml.InftyCDB.normalize_height.create_char_bbox_adjustment import get_latex2adjustment_ratio_list
from pdfxml.InftyCDB.infty_cdb_util import get_glyph_type
from pdfxml.pdf_util.bbox import BBox
from pdfxml.pdf_util.layout_util import get_height, get_width
from pdfxml.InftyCDB.normalize_height.create_char_bbox_adjustment import unify_glyph_type_adjustment_ratio

gt2ur, gt2lr = None, None

###
# load the upper ratio and lower ratio for each type
###
def get_gt2adjust():
    """

    :return: pair of dict, glyph_type 2 upper adjustment, glyph_type 2 lower adjustment
    """
    # TODO, where is this created?
    global gt2ur, gt2lr
    if gt2ur is not None and gt2lr is not None:
        return gt2ur, gt2lr

    #gt_dict = res['gt_dict']    # gt might be short for ground truth
    gt_dict = unify_glyph_type_adjustment_ratio()
    gt2ur_local = {}  # glyph type 2 upper ratio
    gt2lr_local = {}  # glyph type 2 lower ratio
    for gt in gt_dict['code2upper_ratio'].keys():
        gt2ur_local[gt] = np.mean(gt_dict['code2upper_ratio'][gt])
    for gt in gt_dict['code2lower_ratio'].keys():
        gt2lr_local[gt] = np.mean(gt_dict['code2lower_ratio'][gt])
    return gt2ur_local, gt2lr_local


ver_latex2ur, ver_latex2lr, hor_latex2ur, hor_latex2lr = None, None, None, None
def get_latex2adjustment_ratio():
    global ver_latex2ur, ver_latex2lr, hor_latex2ur, hor_latex2lr
    if ver_latex2ur is None or \
            ver_latex2lr is None or \
            hor_latex2ur is None or \
            hor_latex2lr is None:
        gt_dict = get_latex2adjustment_ratio_list()
        ver_latex2ur, ver_latex2lr, hor_latex2ur, hor_latex2lr = {}, {}, {}, {}

        for gt in gt_dict['code2upper_ratio'].keys():
            ver_latex2ur[gt] = np.mean(gt_dict['code2upper_ratio'][gt])
        for gt in gt_dict['code2lower_ratio'].keys():
            ver_latex2lr[gt] = np.mean(gt_dict['code2lower_ratio'][gt])
        for gt in gt_dict['code2upper_ratio_hor'].keys():
            hor_latex2ur[gt] = np.mean(gt_dict['code2upper_ratio_hor'][gt])
        for gt in gt_dict['code2lower_ratio_hor'].keys():
            hor_latex2lr[gt] = np.mean(gt_dict['code2lower_ratio_hor'][gt])
    return ver_latex2ur, ver_latex2lr, hor_latex2ur, hor_latex2lr


def adjust_bbox_h_latex(bbox, latex, debug=False):
    """
    adjust the bbox height based on the latex value

    :param bbox:
    :param latex:
    :param debug:
    :return:
    """
    # based on the latex value, if could not get the value, raise Exception.
    raise Exception("TODO, call the vertically and horizontally separately")
    pass


def get_upper_lower_ratio(latex_val, ver_latex2ur, ver_latex2lr):
    equivalent_classes = [
        ['\\neq', '+'],
    ]
    if latex_val in ver_latex2lr and latex_val in ver_latex2ur:
        return ver_latex2ur[latex_val], ver_latex2lr[latex_val]
    for equivalent_class in equivalent_classes:
        for tmp_latex_val in equivalent_class:
            if tmp_latex_val in ver_latex2ur and tmp_latex_val in ver_latex2lr:
                return ver_latex2ur[tmp_latex_val], ver_latex2lr[tmp_latex_val]
    raise Exception("Could not found equivalent classes")


def adjust_bbox_h_latex_vertically(bbox, latex):
    """

    :param bbox:
    :param latex:
    :return:
    """
    # adjust vertically.
    ver_latex2ur, ver_latex2lr, hor_latex2ur, hor_latex2lr = get_latex2adjustment_ratio()

    #upper_ratio = ver_latex2ur[latex]
    #lower_ratio = ver_latex2lr[latex]
    upper_ratio, lower_ratio = get_upper_lower_ratio(latex, ver_latex2ur, ver_latex2lr)

    new_bbox = copy.copy(bbox)
    if isinstance(new_bbox, BBox):
        new_bbox = new_bbox.to_list()
    else:
        new_bbox = list(new_bbox)

    height = get_height(bbox)
    new_bbox[1] = new_bbox[1] - height * lower_ratio
    new_bbox[3] = new_bbox[3] + height * upper_ratio
    return new_bbox


def adjust_bbox_h_latex_horizontally(bbox, latex):
    """

    :param bbox:
    :param latex:
    :return:
    """
    # adjust horizontally.
    ver_latex2ur, ver_latex2lr, hor_latex2ur, hor_latex2lr = get_latex2adjustment_ratio()
    if latex not in hor_latex2ur or latex not in hor_latex2lr:
        hor_equivalent_map = {
            "\\approx": "=",
            "\\simeq": "=",
        }
        if latex in hor_equivalent_map:
            latex = hor_equivalent_map[latex]
        elif latex.startswith("\\not"):
            latex = "\\backslash"
        else:
            raise Exception("No Stat yet for {}".format(latex))

    upper_ratio = hor_latex2ur[latex]
    lower_ratio = hor_latex2lr[latex]

    new_bbox = copy.copy(bbox)
    if isinstance(new_bbox, BBox):
        new_bbox = new_bbox.to_list()
    else:
        new_bbox = list(new_bbox)

    width = get_width(bbox)
    new_bbox[1] = new_bbox[1] - width * lower_ratio
    new_bbox[3] = new_bbox[3] + width * upper_ratio
    return new_bbox



def adjust_bbox_h_gt(bbox, gt, debug=False):
    """
    width stable character.

    :param bbox:
    :param gt: String of glyph type of xyz
    :return:
    """
    gt2ur, gt2lr = get_gt2adjust()

    upper_ratio = gt2ur[gt]
    lower_ratio = gt2lr[gt]
    if debug:
        print gt, upper_ratio, lower_ratio
    new_bbox = copy.copy(bbox)
    new_bbox = list(new_bbox)
    height = get_height(bbox)
    new_bbox[1] = new_bbox[1] - height*lower_ratio
    new_bbox[3] = new_bbox[3] + height*upper_ratio
    return new_bbox


def adjust_bbox_h_gt_name(bbox, name):
    """
    gt is short for glyph_type

    adjust the height of the bbox given the name

    :param bbox: quadruple
    :param name: should be the unified Latex name
    :return:
    """
    gt = get_glyph_type(name)

    # NOTE, only adjust the one in alphabetic
    if gt not in ['y', 'xy', 'yz', 'xyz', 'hxy', 'hxyz']:
        return bbox
    return adjust_bbox_h_gt(bbox, gt)


if __name__ == "__main__":
    pass
