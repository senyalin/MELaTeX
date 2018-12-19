"""
common statistic functions

 * sampling from a CDF
"""

import numpy as np


class Distribution:
    def __init__(self):
        pass

    def pdf(self, v):
        """

        :param v: the r.v. value
        :return:
        """
        pass

    def cdf(self, v):
        """

        :param v: the value of the r.v.
        :return:
        """
        pass


class GaussianDist(Distribution):
    def __init__(self, mu, sigma):
        """

        :param mu: mean
        :param sigma: standard derivation
        """
        self.mu = mu
        self.sigma = sigma

    def __str__(self):
        return "GaussianDist(mu={}, std={})".format(self.mu, self.sigma)

    def pdf(self, v):
        """
        Probabilistic density function of Gaussian

        :param v: the value to estimate PDF
        :return: scalar value of PDF
        """
        sigma_pow = np.power(self.sigma, 2)
        x_mu_pow = np.power(v-self.mu, 2)
        return 1 / np.sqrt(2 * np.pi * sigma_pow) * np.exp(-1 * x_mu_pow / 2 / sigma_pow)


class SampleDist(Distribution):
    """
    The distribution is non-parametric
    """

    def __init__(self, vlist):
        """
        don't store the original data
        :param vlist:
        """
        #self.vlist = vlist

        from kernel_density_estimation import gen_cdf_model_from_samples, gen_pdf_model_from_samples

        self.cdf_model = gen_cdf_model_from_samples(vlist)
        self.pdf_model = gen_pdf_model_from_samples(vlist)

    def pdf(self, v):
        """
        using the linear interpolation to estimate the pdf value for
            a specific v or list of values

        :param v: v could be a scalar value or a vector
        :return: return type is the same with the input type
        """
        return np.interp(
            v,
            self.pdf_model['xlist'],
            self.pdf_model['ylist'])

    def cdf(self, v):
        return np.interp(
            v,
            self.cdf_model['xlist'],
            self.cdf_model['ylist'])

    def gen_random(self, sample_num=1000):
        """
        numpy random uniform in 0 and 1
            then interpolate back from y to x

        :param sample_num:
        :return:
        """
        u_list = np.random.uniform(size=sample_num)
        y_list = self.cdf_model['ylist']
        x_list = self.cdf_model['xlist']
        samples = np.interp(u_list, y_list, x_list)
        return samples




