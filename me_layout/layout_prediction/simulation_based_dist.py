"""
Create distribution based on simulation
"""
import os
import itertools
import pdfxml.me_layout.me_layout_config as me_layout_config
from pdfxml.file_util import load_serialization, dump_serialization
from pdfxml.path_util import infty_cdb_folder
from pdfxml.me_layout.layout_prediction.common_stat import SampleDist
from pdfxml.InftyCDB.macros import rel_id2rel_str
from pdfxml.InftyCDB.global_model.fea_basis_InftyCDB import get_rel_str2fea_val_list_nycd, get_rel_str2fea_val_list_hr


def get_dist_cache_path(rel_id_list, prefix, sample_num=None):
    """

    :param rel_id_list: list of rel_id to describe the relative position of two chars
    :param prefix: ??
    :param sample_num: the # of samples generated in the simulation to estimate the non-parametric
    :return:
    """

    # rel_list_str = '_'.join([rel_id2rel_str[rel_id] for rel_id in rel_id_list])
    # TO avoid long file path error

    rel_list_str = "_".join([str(rel_id) for rel_id in rel_id_list])
    # TODO, change to rel list ?
    cut_num = 3
    if len(rel_id_list) > cut_num:
        # split into two parts
        first_half = "_".join([str(rel_id) for rel_id in rel_id_list[:3]])
        second_half = "_".join([str(rel_id) for rel_id in rel_id_list[3:]])

        tmp_folder = "{}/fea_val/{}".format(infty_cdb_folder, first_half)
        if not os.path.isdir(tmp_folder):
            os.makedirs(tmp_folder)

        if not sample_num:
            fpath = "{}/dist_{}-{}.pkl".format(
                tmp_folder, prefix, second_half)
        else:
            fpath = "{}/dist_{}-{}-{}.pkl".format(
                tmp_folder, prefix, second_half, sample_num)
    else:
        tmp_folder = "{}/fea_val/simple".format(infty_cdb_folder)
        if not os.path.isdir(tmp_folder):
            os.makedirs(tmp_folder)
        if not sample_num:
            fpath = "{}/dist_{}-{}.pkl".format(
                tmp_folder, prefix, rel_list_str)
        else:
            fpath = "{}/dist_{}-{}-{}.pkl".format(
                tmp_folder, prefix, rel_list_str, sample_num)
    return fpath


def get_l1_samples(rel_id, fea_name):
    """

    :param rel_id:
    :param fea_name:
    :return:
    """
    rel_str = rel_id2rel_str[rel_id]

    if rel_str == "REV_HORIZONTAL":
        rel_str = "HORIZONTAL"  # the same for the current two features

    if fea_name == 'nycd':
        samples = get_rel_str2fea_val_list_nycd()[rel_str]
    elif fea_name == 'hr':
        all_hr = get_rel_str2fea_val_list_hr()
        print all_hr.keys()
        samples = all_hr[rel_str]
    else:
        raise Exception("Unknown")
    return samples


def get_l1_dist(rel_id, fea_name):
    """

    :param rel_id:
    :param fea_name:
    :return:
    """
    cache_path = get_dist_cache_path([rel_id], fea_name)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    samples = get_l1_samples(rel_id, fea_name)
    dist = SampleDist(samples)

    dump_serialization(dist, cache_path)
    return dist


def get_l1_hr_dist(rel_id):
    """

    :param rel_id:
    :return:
    """
    return get_l1_dist(rel_id, "hr")


def get_hr_dist(rel_id_list, refresh=False, sample_num=me_layout_config.default_sample_num, debug=False):
    """

    :param rel_id_list:
    :param refresh:
    :param sample_num:
    :return:
    """
    cache_path = get_dist_cache_path(
        rel_id_list, 'hr_dist', sample_num=sample_num)

    if os.path.isfile(cache_path) and not refresh:
        if debug:
            print cache_path
        return load_serialization(cache_path)

    print "try to calculate {}".format(cache_path)

    dist = None
    if len(rel_id_list) == 0:
        raise Exception("TODO")
    elif len(rel_id_list) == 1:
        dist = get_l1_hr_dist(rel_id_list[0])
    else:
        n = len(rel_id_list)
        mid = int(n/2)
        # NOTE, there should be symbol overlapping of the two intervals
        # but at the relation level, there is no overlapping
        dist1 = get_hr_dist(rel_id_list[0:mid])
        dist2 = get_hr_dist(rel_id_list[mid:])

        print "done dist1 and dist2"

        sample1 = dist1.gen_random(sample_num)
        sample2 = dist2.gen_random(sample_num)

        print "done gen samples"

        vp_list = itertools.product(sample1, sample2)
        samples = [vp[0] * vp[1] for vp in vp_list]
        dist = SampleDist(samples)

        print "done create new dist"

    dump_serialization(dist, cache_path)
    return dist


def get_l1_nycd_dist(rel_id):
    """

    :param rel_id:
    :return:
    """
    return get_l1_dist(rel_id, "nycd")


def get_nycd_dist(rel_id_list, refresh=False, sample_num=me_layout_config.default_sample_num):
    """
    if length of 0 or 1, will not be

    :param rel_id_list:
    :param refresh:
    :param sample_num:
    :return:
    """
    cache_path = get_dist_cache_path(
        rel_id_list, 'nycd_dist', sample_num=sample_num)
    if os.path.isfile(cache_path) and not refresh:
        return load_serialization(cache_path)

    print "try to calculate {}".format(cache_path)
    dist = None
    if len(rel_id_list) == 0:
        raise Exception("Should not be here")
    elif len(rel_id_list) == 1:
        dist = get_l1_nycd_dist(rel_id_list[0])
    else:
        n = len(rel_id_list)
        mid = int(n/2)

        rel_list1 = rel_id_list[0:mid]
        rel_list2 = rel_id_list[mid:]

        nycd_dist_1 = get_nycd_dist(rel_list1)
        nycd_dist_2 = get_nycd_dist(rel_list2)
        hr_dist_1 = get_hr_dist(rel_list1)

        nycd_samples_1 = nycd_dist_1.gen_random(sample_num)
        nycd_samples_2 = nycd_dist_2.gen_random(sample_num)
        hr_samples_1 = hr_dist_1.gen_random(sample_num)

        # first do nycd2 * hr1

        samples = []
        for nycd2, hr1, nycd1 in itertools.product(
                nycd_samples_2, hr_samples_1, nycd_samples_1):
            tmp = nycd2 * hr1 + nycd1
            samples.append(tmp)
        dist = SampleDist(samples)

    dump_serialization(dist, cache_path)
    return dist