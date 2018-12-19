"""
All processing related to Image

This file is related to the visualization of the image.
get_me_fname_bbox

"""

import os

from pdfxml.path_util import infty_cdb_folder, SHARED_FOLDER
from pdfxml.file_util import load_serialization, dump_serialization
from skimage.io import imread
from pythonutil.file_util import test_folder_exist_for_file_path


def fname2shape():
    """
    pre-calculate and store the shape of image file avoid overhead here
    Need this because the vertical coordinate is reversed.

    """
    cache_path = "{}/tmp/im_shape.pkl".format(infty_cdb_folder)
    test_folder_exist_for_file_path(cache_path)

    if os.path.isfile(cache_path):
        return load_serialization(cache_path)
    im2shape = {}
    img_folder = "{}/InftyCDB-1/Images".format(SHARED_FOLDER)
    for fname in os.listdir(img_folder):
        if not fname.endswith("png"):
            continue
        fpath = "{}/InftyCDB-1/Images/{}".format(SHARED_FOLDER, fname)
        im = imread(fpath)
        im2shape[fname] = im.shape
    dump_serialization(im2shape, cache_path)
    return im2shape


