"""
rather than use font level information only,
we also apply the font-val pair level information.
"""
import re
import numpy as np
from pdfminer.layout import LTChar
from pdfxml.loggers import me_extraction_logger
from pdfxml.pdf_util.font_process import get_char_glyph


def create_me_font_val_condprob(font_stat_dict, debug=False):
    """
    create the conditional probability, with add one to avoid zero probability?
    What if there is zero probability? log will not work
    """
    res_dict = font_stat_dict

    font_val_list = res_dict['me_fontval2count'].keys()
    font_val_list.extend(res_dict['nme_fontval2count'].keys())
    font_val_list = set(font_val_list)

    add_delta = 1e-4
    fv2me_cp = {}
    for font_val in font_val_list:
        me_c = res_dict['me_fontval2count'][font_val] if res_dict['me_fontval2count'].has_key(font_val) else 0
        nme_c = res_dict['nme_fontval2count'][font_val] if res_dict['nme_fontval2count'].has_key(font_val) else 0
        me_c += add_delta
        nme_c += add_delta
        fv2me_cp[font_val] = me_c / (me_c+nme_c)

    return fv2me_cp


def get_me_nme_log_prob_font_val(char_list, font_val_confprob, font_condprob, font=None, debug=False):
    """
    if with such information, then make assessment,
    otherwise, use the font level assessment.

    remove the first left parent and last right parent
    """
    # find first the first left parent and last right parent
    ignore_idx_list = []
    for i, char in enumerate(char_list):
        if isinstance(char, LTChar):
            if char.get_text() == "(":
                ignore_idx_list.append(i)
    for i, char in enumerate(reversed(char_list)):
        if isinstance(char, LTChar):
            if char.get_text() == "." or char.get_text() == "," :
                # pass the punctuation
                continue
            if char.get_text() == ")":
                ignore_idx_list.append(len(char_list)-1-i)
    # add digit to the ignore list
    for i, char in enumerate(char_list):
        if isinstance(char, LTChar):
            if re.match("\d", char.get_text()):
                ignore_idx_list.append(i)

    me_log_sum = 0
    nme_log_sum = 0
    for i, char in enumerate(char_list):
        # TODO, add a new rule here, since digit only does not contribute,
        # does not consider digit when make assessment about the ME or NME
        if not isinstance(char, LTChar):
            continue
        if i in ignore_idx_list:
            continue
        fontname = char.fontname
        font_val = (fontname, char.get_text())
        if font_val_confprob.has_key(font_val):
            me_log_sum += np.log(font_val_confprob[font_val])
            nme_log_sum += np.log(1-font_val_confprob[font_val])
        else:
            if font_condprob.has_key(char.fontname):
                me_log_sum += np.log(font_condprob[fontname])
                nme_log_sum += np.log(1-font_condprob[fontname])
            else:
                pass

    if debug:
        tmp_str = ''.join([c.get_text() for c in char_list if isinstance(c, LTChar)])
        me_extraction_logger.debug("work on line: {}".format(tmp_str.encode('utf-8')))
        for c in char_list:
            fontname = c.fontname
            font_val = (fontname, c.get_text())

            glyph_val = get_char_glyph(c, font)
            me_extraction_logger.debug("with font: {}, glyph {}".format(
                c,
                glyph_val.encode("utf-8") if glyph_val is not None else "None"
            ))
            if font_val_confprob.has_key(font_val):
                me_extraction_logger.debug(font_val_confprob[font_val])
        me_extraction_logger.debug("ME Prob: {}, NME Prob: {}".format(
            me_log_sum, nme_log_sum
        ))

    #return me_log_sum > nme_log_sum
    return me_log_sum, nme_log_sum


def check_me_font_val(char_list, font_val_confprob, font_condprob, font=None, debug=False):
    """

    :param char_list:
    :param font_val_confprob:
    :param font_condprob:
    :param font:
    :param debug:
    :return:
    """
    me_log_sum, nme_log_sum = get_me_nme_log_prob_font_val(
        char_list, font_val_confprob, font_condprob, font, debug)
    return me_log_sum > nme_log_sum


if __name__ == "__main__":
    pass
