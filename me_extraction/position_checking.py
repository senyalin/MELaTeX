"""
Based on the relative position to identify the subscript

PHN Model
"""
from pdfxml.loggers import me_extraction_logger
from pdfxml.me_layout.layout_prediction.pos_features import height_ratio_AB, normalized_ycenter_diff_AB
from pdfxml.me_layout.pss_model.pss_dist_nvcd import PSSNVCDDist
from pdfxml.me_layout.pss_model.pss_dist_hr import PSSHRDist
from pdfxml.InftyCDB.macros import REL_SUB


hr_dist = PSSHRDist([REL_SUB])
hr_ratio_range = hr_dist.get_k_sigma_range(2)
nvcd_dist = PSSNVCDDist([REL_SUB])
nvcd_range = nvcd_dist.get_k_sigma_range(2)

def check_word_subscript_exist(word):
    """
    :param word:
    :return:
    """
    found_subscript = False
    for i in range(len(word) - 1):
        # avoid over doing on the in accurate.
        c1 = word[i].get_text()
        c2 = word[i+1].get_text()
        if not (c1.isdigit() or c1.isalpha()):
            continue
        if not (c2.isdigit() or c2.isalpha()):
            continue
        from pdfxml.pdf_util.layout_util import get_height
        if get_height(word[i].bbox) == 0:
            continue

        hr_fea_val = height_ratio_AB(word[i].bbox, word[i + 1].bbox)
        nvcd_fea_val = normalized_ycenter_diff_AB(word[i].bbox, word[i + 1].bbox)
        if hr_ratio_range[0] <= hr_fea_val <= hr_ratio_range[1] and \
                nvcd_range[0] <= nvcd_fea_val <= nvcd_range[1]:
            found_subscript = True
            me_extraction_logger.debug(
                "{} Bbox1:{}, {} Bbox2:{}".format(
                    word[i].get_text().encode('utf-8'),
                    word[i].bbox,
                    word[i + 1].get_text().encode('utf-8'),
                    word[i + 1].bbox))
    return found_subscript



