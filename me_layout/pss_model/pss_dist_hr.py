"""
height ratio distribution
"""
import numpy as np

from pdfxml.me_layout.pss_model.pss_inftycdb import gamma_sub, gamma_sup, sigma
from pdfxml.me_layout.pss_model.pss_common import get_lognorm_pdf
from pdfxml.InftyCDB.macros import REL_H, REL_SUB, REL_SUP, REV_REL_SUP, REV_REL_SUB, REV_REL_H


class PSSHRDist:
    """
    distribution of position and shift of script model for height ratio
    """

    def __init__(self, rel_list):
        ratio = 1
        rel2ratio = {
            REL_H: 1.0,
            REL_SUB: gamma_sub,
            REL_SUP: gamma_sup,
            REV_REL_H: 1.0,
            REV_REL_SUB: 1.0/gamma_sub,
            REV_REL_SUP: 1.0/gamma_sup}
        for rel in rel_list:
            ratio *= rel2ratio[rel]
        self.mean = np.log(ratio)
        self.sigma = np.sqrt(2)*sigma

    def pdf(self, val, debug=False):
        """
        given a feature value, calculate its probability density

        :param val:
        :return:
        """
        if debug:
            print "HR pdf: mean:{}, std:{}, val:{}".format(self.mean, self.sigma, val)
        return get_lognorm_pdf(val, self.mean, self.sigma)

    def get_k_sigma_range(self, k):
        """
        3 sigma is nearly 99%
        1 sigma is already 95%

        :param k:
        :return:
        """
        # The sigma is after take the log value
        return np.exp(self.mean-k*self.sigma), np.exp(self.mean+k*self.sigma)


rel_list_str2pss = {}

def get_pss_hr_dist(rel_list):
    """
    manager of the nvcd feature distrubtion of different relation list

    :param rel_list:
    :return:
    """
    rel_list_str = '_'.join([str(rel) for rel in rel_list])
    if rel_list_str not in rel_list_str2pss:
        rel_list_str2pss[rel_list_str] = PSSHRDist(rel_list)
    return rel_list_str2pss[rel_list_str]
