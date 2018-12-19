"""
character process
"""
import os
import re
import string
import numpy as np
from pdfminer.layout import LTChar, LTAnno
from pdfxml.loggers import general_logger, pdf_util_error_log
from pdfxml.file_util import load_serialization, dump_serialization
from pdfxml.pdf_util.bbox import BBox
from pdfxml.pdf_util.exceptions import UnknownGlyphName
from pdfxml.pdf_util.font_process import get_char_glyph
from pdfxml.pdf_util.layout_util import merge_bbox_list
from pdfxml.me_taxonomy.math_resources import get_latex_commands, special_unicode_chars, unicode2latex
from pdfxml.InftyCDB.name2latex import name2latex
debug = True


def get_one_ltchar():
    from pdfxml.pdf_util.pdf_extract import process_pdf_internal
    from pdfxml.path_util import ME_RESOURCE_FOLDER
    cache_path = "{}/one_ltchar.pkl".format(ME_RESOURCE_FOLDER)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    pdf_file_name = "{}/NIPS_2016_6202".format(ME_RESOURCE_FOLDER)
    pdf_path = "{}.pdf".format(pdf_file_name)
    char_list = process_pdf_internal(pdf_path, 0)
    dump_serialization(char_list[0], cache_path)

    return char_list[0]


def get_median_char_height_by_char_list(char_list):
    height_list = [BBox(char.bbox).height() for char in char_list if isinstance(char, LTChar)]
    return np.median(height_list)


def get_latex_val_of_gn(gn):
    if gn.startswith("\\"):
        return gn

    if gn is None:
        pdf_util_error_log.error("Failed to get the glyph name")
        raise Exception("Could not get glyph Name")

    if gn in string.lowercase:
        return gn
    if gn in string.uppercase:
        return gn
    if gn in ['-', '%', '.', ';', ',', ':']: # some normal chars
        return gn
    if len(gn) == 1 and ord(gn) < 128:
        return gn

    if gn == "ignore" or gn == "badwindows":
        general_logger.error("Should not return ignore")
        return "bad_val"

    if gn is None:
        general_logger.error("glyph name should not be None")
        tmp = 1

    latex_command = get_latex_commands()
    if gn in latex_command:
        return "\\"+gn
    if gn in name2latex:
        return name2latex[gn]

    # NOTE: to be abandoned, or just separate the math from the other
    if gn in special_unicode_chars:
        return gn

    if isinstance(gn, unicode):
        if gn in unicode2latex:
            return unicode2latex[gn]

    elif isinstance(gn, str):
        tmp_gn = gn
        if tmp_gn in unicode2latex:
            return unicode2latex[tmp_gn]

    # TODO, some special chars?
    if gn in ['circlecopyrt']:
        if gn == 'circlecopyrt':
            return 'R'
        return gn

    if gn.endswith('script'):
        letter = gn[:-6]
        if len(letter) == 1:
            return "\\mathcal{{{}}}".format(letter)

    if re.match(r"\d+", gn) and int(gn) < 256:
        v = int(gn)
        return chr(v)

    # the font does not provide further information
    if re.match(r"[#A-Za-z]{0,2}\d*", gn):
        return gn

    # bad names should not have latex values
    invalid_gn_for_latex =[
        'null',     # might be pdfbox processing error
        'heart',    # might be the poker symbol
        'section',  # to indicate the reference, not as ME
        '.notdef',  # bad
        'ESC', 'FF', 'VT', 'BS', 'ETB', 'HT', 'SO',

        # arabic character
        'chard5', 'charce', 'charab', 'char0b', 'char58',

        # old english letters
        'Eth',

        # some others
        #https://www.w3.org/TR/MathML2/isonum.html
        'yen', 'trademark', 'currency',
        'guillemotleft', 'guillemotright',

        # TODO,
        'owner', 'squash',

        # special font type
        'weierstrass',

        # TODO, need to check where, they are mostly math concept here
        'power', 'norm', 'abs', 'divide', 'softmax', 'plus-or-minus',
        'notforcesextra', 'nottriangeqlleft', #10.1.1.1.2077_5
        'squareimage', #10.1.1.1.2105_5
        'arrowvertex', 'arrowbt', 'wreathproduct', #10.1.1.138.4863_11
        'twosuperior',  # 10.1.1.193.1818_2
        'ring',  # 10.1.1.6.2202_3
        'satisfies', 'notturnstile', 'forces', 'notforces',  # 10.1.1.6.2246_15
        'squiggleright',  # 10.1.1.6.2302_13
        'ordmasculine',  # 10.1.1.6.2330_13

    ]
    if gn in invalid_gn_for_latex:
        return ''
    from pdfxml.me_taxonomy.math_resources import func_name_list
    if gn in func_name_list:
        return gn

    print gn.encode('hex')
    #raise Exception("Unknown"+gn)
    pdf_util_error_log.error("Unknown "+gn.encode('utf-8', 'ignore'))
    raise UnknownGlyphName(gn)


def is_space_char(char):
    """
    :param char:
    :return:
    """
    if isinstance(char, LTAnno):
        return True
    if isinstance(char, LTChar) and char.get_text() in [' ', 'space']:
        return True
    return False


def get_latex_val_of_lt_char(c, font_dict=None):
    """
    lt_char is for lTChar, which is the data type defined by pdfminer

    The latex value is determined based on the combination of information
    from the latex command and the glyph name

    :param font_dict: dict from font name to list of the triples
    :type font_dict: dict(str, list(tuple))
    :param c: one character
    :type c: LTChar
    :return:
    """
    assert isinstance(c, LTChar)
    if font_dict is None:  # assume already in glyph name
        gn = c.get_text()
        return get_latex_val_of_gn(gn)
        #return gn
    else:
        gn = get_char_glyph(c, font_dict, debug)
        return get_latex_val_of_gn(gn)


def unify_glyph_name(glyph_name):
    latex_commands = get_latex_commands()
    if glyph_name in latex_commands:
        return glyph_name

    # if english alphabet
    if len(glyph_name) == 1:
        if re.match(r"[A-Za-z]", glyph_name):
            return glyph_name

    extra_names = [
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
        'equal',
        'colon', 'comma', 'period']
    if glyph_name in extra_names:
        return glyph_name

    g2l = {
        'braceleft': 'MiddleLeftPar',
        'braceright': 'MiddleRightPar',
        'parenleft': 'LeftPar',
        'parenright': 'RightPar',
        'element': 'in',
    }
    if not g2l.has_key(glyph_name):
        raise Exception("Could not found matching for {}".format(glyph_name))
    return g2l[glyph_name]


def adjust_char_bbox_by_path(lines, paths):
    for li, line in enumerate(lines):
        for ci, char in enumerate(line):
            if not isinstance(char, LTChar):
                continue
            for path in paths:
                path_bbox = BBox(path.bbox)
                char_bbox = BBox(char.bbox)
                if char_bbox.overlap(path_bbox):
                    path_bbox_v_center = path_bbox.v_center()
                    path_bbox_height = path_bbox.height()
                    path_bbox_height += 1
                    bbox1, bbox2 = char_bbox.v_split(path_bbox_v_center, path_bbox_height * 1.1 / 2)
                    if bbox1.area() > bbox2.area():
                        lines[li][ci].set_bbox(bbox1.to_list())
                    else:
                        lines[li][ci].set_bbox(bbox2.to_list())
    return lines


def simplify_glyph(val):
    """
    the glyph is only for non english chars

    :param val:
    :return:
    """
    from pdfxml.InftyCDB.name2latex import normal_fence_mapped
    # TODO, the bracket, parenthesis, brace as curve bracket

    name2char = {
        'period': '.',
        'comma': ',',
        'colon': ':',
        'space': ' ',

        'zero': '0',
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9',

        #'equal': '=',
        #'greater': '>',
        #'less': '<',
    }

    if val in name2char:
        return name2char[val]
    if val in normal_fence_mapped:
        return normal_fence_mapped[val]
    return val


def char_list2str(char_list, delimiter=''):
    """

    :param char_list:
    :param delimiter:
    :return:
    """
    # UnicodeDecodeError: 'ascii' codec can't decode byte 0xef in position 0: ordinal not in range(128)
    try:
        return delimiter.join([c.get_text() for c in char_list])
    except Exception as e:
        tmp_str = ""
        for c in char_list:
            tmp_val = c.get_text()
            try:
                tmp_str += delimiter+tmp_val
            except Exception as e2:
                print e2
        return tmp_str


def char_list2bbox(char_list):
    bbox_list = [char.bbox for char in char_list if isinstance(char, LTChar)]
    return merge_bbox_list(bbox_list)


def check_sorted_by_left(char_list):
    """
    check whether the char_list is sorted by the left boundary

    :param char_list:
    :return:
    """
    if len(char_list) == 0:
        return True
    cur_left = None
    i = 0
    while i < len(char_list):
        if isinstance(char_list[i], LTChar):
            if cur_left is None:
                cur_left = char_list[i].bbox[0]
            else:
                if char_list[i].bbox[0] < cur_left:
                    return False
        i += 1
    return True

