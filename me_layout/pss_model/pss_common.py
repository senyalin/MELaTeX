"""

"""
import numpy as np


def get_lognorm_pdf(val, mu, sigma):
    """

    :param val:
    :param mu:
    :param sigma:
    :return:
    """
    #assert val > 0
    if val <= 0:
        return np.finfo(np.float64).tiny
    log_val = np.log(val)
    exp_num = -1.0 * np.power(log_val - mu, 2) / 2 / np.power(sigma, 2)
    res = 1.0 / val / sigma / np.sqrt(2 * np.pi) * np.exp(exp_num)
    if res == 0:
        return np.finfo(np.float64).tiny
    return res