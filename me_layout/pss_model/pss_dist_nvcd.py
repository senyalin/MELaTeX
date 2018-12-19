"""
pss model for normalized vertical center difference
"""
import numpy as np

from pdfxml.me_layout.pss_model.pss_inftycdb import gamma_sub, gamma_sup, delta_sup, delta_sub, theta_b, sigma
from pdfxml.me_layout.pss_model.pss_common import get_lognorm_pdf
from pdfxml.InftyCDB.macros import REL_H, REL_SUB, REL_SUP, REV_REL_SUP, REV_REL_SUB, REV_REL_H


class PSSNVCDDist:
    """

    """
    def __init__(self, rel_list):
        # save the rel_list for debugging
        self.rel_list = rel_list

        cur_h = 1
        base = cur_h*theta_b
        rel2ratio = {
            REL_H: 1.0,
            REV_REL_H: 1.0,
            REL_SUB: gamma_sub,
            REL_SUP: gamma_sup,
            REV_REL_SUB: 1.0 / gamma_sub,
            REV_REL_SUP: 1.0 / gamma_sup}

        for rel in rel_list:

            if rel == REL_SUB:
                base += cur_h*delta_sub

            elif rel == REL_SUP:
                base += cur_h*delta_sup

            elif rel == REV_REL_SUB:
                base -= cur_h/gamma_sub*delta_sub

            elif rel == REV_REL_SUP:
                base -= cur_h/gamma_sup*delta_sup

            elif rel in [REL_H, REV_REL_H]:
                pass

            else:
                raise Exception("Unknown relation")
            cur_h *= rel2ratio[rel]

        self.mean = np.log(cur_h)
        self.sigma = np.sqrt(2) * sigma
        self.last_base = base  # the baseline of the char

    def __str__(self):
        return "mean {}, std {}, base {}".format(self.mean, self.sigma, self.last_base)

    def pdf(self, val, debug=False):
        """
        the normalized height ratio

        :param val: given the feature value, calculate the probabilty
        :return:
        """
        n_val = (val - (self.last_base-0.5)) / (0.5-theta_b)
        if debug:
            print "NVCD PDF: last base as {}, theta_b as {}, cur_val {}".format(
                self.last_base, theta_b, val)
            print "NVCD PDF: mean {}, std {}, val {}".format(
                self.mean, self.sigma, n_val)
        return get_lognorm_pdf(n_val, self.mean, self.sigma)

    def get_k_sigma_range(self, k):
        lower_bound = np.exp(self.mean-k*self.sigma)
        upper_bound = np.exp(self.mean+k*self.sigma)
        shifted_lb = lower_bound*(0.5-theta_b)+(self.last_base-0.5)
        shifted_up = upper_bound*(0.5-theta_b)+(self.last_base-0.5)
        return shifted_lb, shifted_up


rel_list_str2pss = {}


def get_pss_nvcd_dist(rel_list):
    """
    manager of the nvcd feature distrubtion of different relation list

    On the ICST dataset, check the fitness of the height for lognormal distribution.
    Still does not fit, but the trends is OK. Might be due to the limitation on the # of sample files
    Could get more files to do such statistics.

    Based on my inference, the NVCD feature is a shift of the height ratio feature.
    \theta_b: baseline-descender diff / ascender-descender diff (i.e. height)
    \delta_SUB/SUP: the drop-off ratio, or raise up ratio of the script

    :param rel_list:
    :return:
    """
    rel_list_str = '_'.join([str(rel) for rel in rel_list])
    if rel_list_str not in rel_list_str2pss:
        rel_list_str2pss[rel_list_str] = PSSNVCDDist(rel_list)
    return rel_list_str2pss[rel_list_str]
