"""
This is independent of the data set to create such mapping

The mapping from data specified value to latex is done in each dataset

One thing I did not realize before is that this adjustment
might only work for the alphanumeric symbols, which is also
what Okomoto is doing.

TODO, many resource overlapping with the InftyCDB.marcos
"""
import string

from pdfxml.InftyCDB.normalize_height.char_adjust_bbox import adjust_bbox_h_gt, adjust_bbox_h_latex_horizontally, \
    adjust_bbox_h_latex_vertically

# TODO, load the adjustment resource
from pdfxml.me_taxonomy.glyph.glyph_shape_type import get_gt_type_by_latex_val, \
    GT_HEIGHT_STABLE, GT_WIDTH_STABLE, GT_CENTERED, GT_NON_STABLE

from pdfxml.InftyCDB.name2latex import name2latex
from pdfxml.pdf_util.bbox import BBox

# TODO, the function and adjustment should be separated.
from pdfxml.me_taxonomy.latex.latex_glyph import xy_greek_list, y_greek_list, xyz_greek_list, yz_greek_list, greek_list, \
    greek_name_list
from pdfxml.me_taxonomy.latex.latex_glyph import y_list, xy_list, yz_list, xyz_list, hxy_list, hxyz_list

xy_list = xy_list+"0123456789"

gt2symbol_list = {
    "y_list": y_list,
    "xy_list": xy_list,
    "yz_list": yz_list,
    "xyz_list": xyz_list,
    "hxy_list": hxy_list,
    "hxyz_list": hxyz_list,
    "xy_greek_list": xy_greek_list,
    "y_greek_list": y_greek_list,
    "xyz_greek_list": xyz_greek_list,
    "yz_greek_list": yz_greek_list
}


def get_glyph_type_by_latex_val(latex_val):
    the_gt = None
    for gt, symbol_list in gt2symbol_list.items():
        if latex_val in symbol_list:
            the_gt = gt[:gt.index("_")]
            break
    return the_gt


def adjust_bbox_by_latex_val(bbox, latex_val):
    """
    Given the tight bbox of a char and the latex value,

    :param bbox: tight bbox
    :type bbox: BBox
    :param latex_val: string of the latex
    :return:
    """
    if latex_val in ["\\prime", "\\dprime"]:
        # find
        return bbox

    if latex_val.startswith("\\mathcal"):
        latex_val = latex_val[latex_val.index("{")+1: latex_val.index("}")]

    # TODO, find the stat
    glyph_type = get_gt_type_by_latex_val(latex_val)
    if glyph_type == GT_NON_STABLE:
        return BBox(bbox)
    elif glyph_type == GT_HEIGHT_STABLE:
        # adjust by the character
        return adjust_bbox_h_latex_vertically(bbox, latex_val)
    elif glyph_type == GT_CENTERED:
        return BBox(bbox)
    elif glyph_type == GT_WIDTH_STABLE:
        return adjust_bbox_h_latex_horizontally(bbox, latex_val)
    else:
        print type(bbox)
        raise Exception("unknown type for bbox")


def is_adjustable_by_latex_val(latex_val):
    """
    TODO,
    :param latex_val:
    :return:
    """
    if latex_val is None:
        return False
    if not latex_val.startswith("\\"):
        if latex_val not in name2latex:
            return False
        latex_val = name2latex[latex_val]

    gt = get_glyph_type_by_latex_val(latex_val)
    return gt is not None


def can_calculate_center_by_latex_val(latex_val):
    """

    :param latex_val:
    :return:
    """
    from pdfxml.me_taxonomy.math_resources import accent_name_list, under_name_list
    val = latex_val if not latex_val.startswith("\\") else latex_val[1:]
    if val in accent_name_list:
        return False
    if val in under_name_list:
        return False
    if val in ['\\prime', "'", "''", '\\dprime']:
        return False

    if latex_val in [",", ".", "\\ldots"]:
        return False
    return True


def can_cal_center(me_symbol):
    if me_symbol is None:
        return False
    return can_calculate_center_by_latex_val(me_symbol.latex_val)


#############
# interface to determine the type of the symbol
#############

def is_regular_shaped_for_glyph(glyph_name):
    """
    NOTE, this is for the ME layout analysis

    digits, letters, and greek

    :param glyph_name:
    :return:
    """
    from pdfxml.me_taxonomy.glyph.glyph_shape_type import get_gt_type_by_latex_val, GT_HEIGHT_STABLE, GT_WIDTH_STABLE
    from pdfxml.me_taxonomy.glyph.glyph2latex import get_latex_by_glyph
    latex = get_latex_by_glyph(glyph_name)
    gt_type = get_gt_type_by_latex_val(latex)
    if gt_type == GT_HEIGHT_STABLE or gt_type == GT_WIDTH_STABLE:
        return True
    return False


def could_estimate_height(me_obj):
    """
    regular shaped means the height could be estimated.
    :param me_obj:
    :return:
    """

    if isinstance(me_obj, MESymbolGroup):
        return is_regular_shaped_for_glyph(me_obj.me_symbol.latex_val)
    elif isinstance(me_obj, MESymbol):
        return is_regular_shaped_for_glyph(me_obj.latex_val)
    elif isinstance(me_obj, str) or isinstance(me_obj, unicode):
        return is_regular_shaped_for_glyph(me_obj)
    elif me_obj is None:
        return False
    else:
        print me_obj
        raise Exception("TODO")


def could_calculate_center_by_glyph(glyph_name):
    """
    NOTE, this is for the ME layout analysis

    :param glyph_name:
    :return:
    """
    if glyph_name.startswith('\\'):
        glyph_name = glyph_name[1:]

    glyph_name = glyph_name.strip()

    if is_regular_shaped_for_glyph(glyph_name):
        return True

    good_glyph_name_list = [
        'sum', 'int', 'bigoplus', 'odot',
        'prod', 'coprod', # 28018198

        #'\\prod', TODO? base line reliable?

        '(', ')', '{', '}', '[', ']', 'rangle', 'langle',
        'Bigl(', 'bigl(', 'bigr)', 'Bigr)',
        'MiddleLeftPar', 'MiddleRightPar', 'BigLeftPar', 'BigRightPar', 'LeftPar', 'RightPar',
        '=', '-', '+', '/', 'divide', 'otimes', 'circ', 'slash', 'backslash', 'plus', 'minus', 'pm', 'oplus', 'times', 'rtimes',
        'approx', 'less', 'equiv',  'leqq', 'simeq', 'leq', 'equal', 'notequiv', 'subset', 'sim', 'notequal', 'cong',
        'mapsto',
        'nsubseteq', 'subsetnoteqq', 'subseteq', 'supsetnoteqq', 'in', 'notin', 'ni', 'supseteq', 'notsubset', 'supset',
        'Rightarrow', 'Leftrightarrow', 'hookrightarrow', 'leftarrow', 'rightarrow',
        'preceq', '<', 'prec', 'preceq',
        'geq', '>', 'gg', 'geqq', 'greater', 'succ', 'geq', 'succeq',
        'cdots', 'cdot',
        'emptyset', 'infty', 'square',
        'ContinuedFraction', 'fractionalLine', 'hyphen', 'longHyphen',
        'bullet', 'colon', 'semicolon', 'sharp', ':', ';', 'textopenbullet', 'openbullet'
        'neg',
        '|', 'bar', "||",
        "frac",
    ]

    bad_glyph_name_list = [
        ',', '.', 'comma', 'period', 'ldots', 'prime', 'dprime', 'doubleprime',  # punct
        'tilde', 'overline', 'vec', 'underline', 'underbrace', 'check', 'hat', 'dot',    # accent

        'coprod', 'prod', 'cup', 'cap', 'bigcap', 'bigcup', 'vee', 'bigwedge', 'wedge',   # varying size non-centered.
        'lfloor', 'rfloor', 'sqrt', 'vert',  # varying size non-centered

        'ast',  'star',  # uncertain because could be place on the superscript
        'degree',

        'downarrow', 'varpitchfork', 'smile',  'SingleEndQuartation', 'nmid'  # unsure
    ]

    if glyph_name in good_glyph_name_list:
        return True
    if glyph_name in bad_glyph_name_list:
        return False
    if glyph_name.startswith("not") and "\\" in glyph_name:
        return True

    raise Exception("unknown glyph name '{}'".format(glyph_name))


def could_calculate_center(me_obj):
    from pdfxml.me_layout.me_group.atomic_me_group import MESymbolGroup
    from pdfxml.me_layout.me_group.me_group import MESymbol

    if isinstance(me_obj, MESymbolGroup):
        return could_calculate_center_by_glyph(me_obj.me_symbol.latex_val)
    elif isinstance(me_obj, MESymbol):
        return could_calculate_center_by_glyph(me_obj.latex_val)
    elif isinstance(me_obj, str) or isinstance(me_obj, unicode):
        return could_calculate_center_by_glyph(me_obj)
    elif me_obj is None:
        return False
    else:
        raise Exception("TODO")


def center_line_overlapping_checking(base_me_group, target_me_group):
    """
    check whether the center line of the target_me_group
    lies in the center range of the base_me_group

    :param base_me_group:
    :param target_me_group:
    :return:
    """
    # if the primiary character of base_me_group is with normalized shaped.
    base_me_symbol = base_me_group.get_baseline_symbol()
    target_me_symbol = target_me_group.get_baseline_symbol()

    if base_me_symbol is None or target_me_symbol is None:
        return False

    if isinstance(base_me_symbol, MESymbol) and isinstance(target_me_symbol, MESymbol):
        # check whether the based_me_group is regular shaped.
        base_regular_shape = could_estimate_height(base_me_symbol)
        target_centered = could_calculate_center(target_me_symbol)
        if base_regular_shape and target_centered:
            # check whether the center of the target ME is in the center band of the base ME
            base_h = base_me_group.get_adjust_height()
            baser_v_c = base_me_group.get_v_center()
            target_v_c = target_me_group.get_v_center()
            if baser_v_c-base_h*me_layout_config.center_band_threshold <= target_v_c <= \
                    baser_v_c+base_h*me_layout_config.center_band_threshold:
                return True
            else:
                return False
        else:
            from pdfxml.loggers import me_analysis_logger
            me_analysis_logger.debug("could not decide symbol pair {} {}".format(base_me_group, target_me_group))
            return False

    else:
        raise Exception(
            "TODO unknown to process two group of type {} and {}".format(
                type(base_me_group), type(target_me_group)
            )
        )


if __name__ == "__main__":
    pass
