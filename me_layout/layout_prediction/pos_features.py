"""
TODO, add more features given the review from publication.

"""
import numpy as np

from pdfxml.pdf_util.layout_util import merge_bbox, \
    get_height, get_width, get_y_center, get_x_center, get_center

shape_paper_list = [
    "height_ratio_AB",
    "normalized_ycenter_diff_AB",
    "normalized_Ar_Bl_diff_by_height_AB",
    "normalized_Al_Bl_diff_by_height_AB",
    "normalized_Ar_Br_diff_by_height_AB",
    "normalized_Ab_Bt_diff_by_height_AB",
    "normalized_At_Bt_diff_by_height_AB",
    "normalized_Ab_Bb_diff_by_height_AB"
]


####
# shape paper
####
def height_ratio_AB(b1, b2):
    """
    height ratio
    """
    return get_height(b2) / get_height(b1)


def normalized_ycenter_diff_AB(b1, b2):
    """
    vertical center difference normalized by height of first bbox
    """
    return (get_y_center(b2)-get_y_center(b1))/get_height(b1)


def normalized_xcenter_diff_by_height_AB(b1, b2):
    """
    horizontal center difference normalized by height of first bbox
    """
    x_center_diff = get_x_center(b1) - get_x_center(b2)
    return x_center_diff/get_height(b1)


def normalized_Ar_Bl_diff_by_height_AB(b1, b2):
    d = b2[0] - b1[2]
    return d/get_height(b1)


def normalized_Al_Bl_diff_by_height_AB(b1, b2):
    d = b2[0] - b1[0]
    return d/get_height(b1)


def normalized_Ar_Br_diff_by_height_AB(b1, b2):
    d = b2[2] - b1[2]
    return d/get_height(b1)


def normalized_Ab_Bt_diff_by_height_AB(b1, b2):
    d = b2[3] - b1[1]
    return d/get_height(b1)


def normalized_At_Bt_diff_by_height_AB(b1, b2):
    d = b2[3]-b1[3]
    return d/get_height(b1)


def normalized_Ab_Bb_diff_by_height_AB(b1, b2):
    d = b2[1]-b1[1]
    return d/get_height(b1)

####
#
####
other_features = [
    "normalized_At_Bb_diff_by_height_AB",
    "normalized_Ar_Bl_diff_by_width_AB",
    "h_overlap_ratio",
    "v_overlap_ratio",
    "normalized_xcenter_diff_by_merge_AB",
    "normalized_ycenter_diff_by_merge_AB"
]


def normalized_At_Bb_diff_by_height_AB(b1, b2):
    d = b2[1]-b1[3]
    return d/get_height(b1)


def normalized_Ar_Bl_diff_by_width_AB(b1, b2):
    d = b2[0] - b1[2]
    return d/get_width(b1)


def h_overlap_ratio(b1, b2):
    """
    horizontal overlapping ratio
    """
    #b1[0], b1[2]
    common_left = np.max( (b1[0], b2[0]) )
    common_right = np.min( (b1[2], b2[2]) )
    common = np.max( (0, common_right-common_left) )

    merge_left = np.min( (b1[0], b2[0]) )
    merge_right = np.max( (b1[2], b2[2]) )
    #print common, merge_left, merge_right
    return common / (merge_right-merge_left)


def v_overlap_ratio(b1, b2):
    """
    vertical overlapping ratio
    """
    common_b = np.max( (b1[1], b2[1]) )
    common_t = np.min( (b1[3], b2[3]) )
    common = np.max( (0, common_t-common_b) )
    merge_b = np.min( (b1[1], b2[1]) )
    merge_t = np.max( (b1[3], b2[3]) )
    return common / (merge_t-merge_b)


def normalized_xcenter_diff_by_merge_AB(b1, b2):
    """
    symmetric horizontal difference
    """
    mb = merge_bbox(b1, b2)
    return abs(get_x_center(b1) - get_x_center(b2)) / get_width(mb)


def normalized_ycenter_diff_by_merge_AB(b1, b2):
    """
    symmetric vertical difference
    """
    mb = merge_bbox(b1, b2)
    return abs(get_y_center(b1)-get_y_center(b2)) / get_height(mb)

#######
# probabilistic SVMs and stochastic context free grammars
#######
def center_angle_AB(b1, b2):
    x1, y1 = get_center(b1)
    x2, y2 = get_center(b2)
    if x1 != x2:
        tan_val = (y2-y1)/(x2-x1)
        #print tan_val
        return np.arctan(tan_val)
    else:
        return np.pi/2

#####
# summary all
#####
fea_name_list = []
fea_name_list.extend(shape_paper_list)
fea_name_list.extend(other_features)
fea_name_list.append("center_angle_AB")

fea_func_list = [globals()[func_name] for func_name in fea_name_list]
fea_name2fea_func = {fea_name:fea_func for fea_name, fea_func in zip(fea_name_list, fea_func_list)}


def test_feature():
    bbox1 = [2355.0, 3827.0, 2374.0, 3849.0] # sup
    bbox2 = [2319.0, 3658.0, 2341.0, 3864.0] # parent right
    for fea_name, fea_func in zip(fea_name_list, fea_func_list):
        print fea_func
        print fea_name, fea_func(bbox1, bbox2)


if __name__ == '__main__':
    test_feature()
