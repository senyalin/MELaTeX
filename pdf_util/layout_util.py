"""
utility functions for layout analysis
bbox : (left, bottom, right, top)
"""
import numpy as np
from pdfxml.pdf_util.bbox import BBox
from pdfminer.layout import LTChar, LTRect, LTLine

# gradually move to BBox class
"""
def get_left(bbox):
    return bbox[0]

def get_right(bbox):
    return bbox[2]

def get_bottom(bbox):
    return bbox[1]

def get_top(bbox):
    return bbox[3]
"""


def get_height(bbox):
    if isinstance(bbox, BBox):
        return bbox.height()
    else:
        return bbox[3]-bbox[1]


def get_width(bbox):
    if isinstance(bbox, BBox):
        return bbox.width()
    else:
        return bbox[2]-bbox[0]


def get_y_center(bbox):
    if isinstance(bbox, BBox):
        return bbox.v_center()
    else:
        return (bbox[3]+bbox[1])/2


def get_x_center(bbox):
    return (bbox[2]+bbox[0])/2


def get_center(bbox):
    return get_x_center(bbox), get_y_center(bbox)


# char functions
def get_char_x_mean(c):
    return get_x_center(c.bbox)


def get_char_y_mean(c):
    return get_y_center(c.bbox)

def get_char_mean(c):
    return (get_char_x_mean(c), get_char_y_mean(c))


def bbox_rescale(bbox, r):
    """
    rescale the bbox based on the ratio
    """
    return [v*r for v in bbox]


def char_in_bbox(c, bbox):
    if not isinstance(c, LTChar):
        return False
    x, y = get_char_mean(c)
    if x > bbox[0] and x < bbox[2] and y > bbox[1] and y < bbox[3]:
        return True
    return False

def char_in_bbox_list(c, bbox_list):
    for bbox in bbox_list:
        if char_in_bbox(c, bbox):
            return True
    return False


def get_chars_in_bbox(cand_chars, bbox, rescale=1):
    new_bbox = [rescale*e for e in bbox]
    #print new_bbox
    res = [c for c in cand_chars if char_in_bbox(c, new_bbox)]
    return res


def get_paths_in_bbox(cand_paths, bbox, rescale=1):
    new_bbox = [rescale*e for e in bbox]
    res = [p for p in cand_paths if bbox_within(get_xpath_bbox(p) , new_bbox)]
    return res


#########
# Bbox related function
#########
def bbox_area(bbox):

    return (bbox[2]-bbox[0])*(bbox[3]-bbox[1])

def valid_bbox(bbox):
    if bbox[0] < 0 or bbox[1] < 0 or bbox[2] < 0 or bbox[3] < 0:
        return False
    if bbox[0] > bbox[2]:
        return False
    if bbox[1] > bbox[3]:
        return False
    return True


def bbox_overlap(b1, b2):
    """

    :param b1:
    :param b2:
    :return:
    """
    if isinstance(b1, tuple) or isinstance(b1, list):
        if b2[2] < b1[0]:
            return False
        if b2[0] > b1[2]:
            return False
        if b2[1] > b1[3]:
            return False
        if b2[3] < b1[1]:
            return False
        return True
    else:
        return b1.overlap(b2)


def bbox_overlap_area(b1, b2):
    """
    get the overlapping area
    """
    if isinstance(b1, tuple) or isinstance(b1, list):
        l = max(b1[0], b2[0])
        r = min(b1[2], b2[2])
        t = min(b1[3], b2[3])
        d = max(b1[1], b2[1])
        if r>l and t>d:
            return (r-l)*(t-d)
        else:
            return 0
    else:
         return b1.intersect(b2).area()


def bbox_overlap_list(b, blist):
    for nb in blist:
        if bbox_overlap(b, nb):
            return True
    return False


def max_overlap_area_bbox_bboxlist(b, blist):
    max_area = 0
    for nb in blist:
        if not bbox_overlap(b, nb):
            continue
        tmp_area = bbox_overlap_area(b, nb)
        max_area = max(max_area, tmp_area)
    return max_area


def bbox_half_overlap_list(b, blist, thres=0.5):
    """
    return true if there is a bbox in blist that overlap area > thres * b.area

    :param b:
    :param blist:
    :param thres:
    :return:
    """
    b = BBox(b)
    org_area = b.area()
    for nb in blist:
        if not b.overlap(nb):
            continue
        ol_area = b.intersect(nb).area()
        # ol_area = bbox_overlap_area(b, nb)
        if ol_area > org_area*thres:
            return True
    return False


def get_bbox_mean(b):
    """

    :param b:
    :return:
    """
    x = (b[0] + b[2])/2
    y = (b[1] + b[3])/2
    return x, y


def bbox_center_within(b1, b2):
    """
    check whether center of bbox 1 is within the bbox2
    bbox (left, bottom, right, top)
    """
    x, y = get_bbox_mean(b1)
    if x > b2[0] and x < b2[2] and y > b2[1] and y < b2[3]:
        return True
    return False

def bbox_center_within_any(b1, b_list):
    """
    check whether center of bbox 1 is within the bbox2
    bbox (left, bottom, right, top)
    """
    for b2 in b_list:
        if bbox_center_within(b1, b2):
            return True
    return False

def bbox_within(b1, b2):
    """
    bounding box b1 in the bounding box b2
    """
    if b1[0] < b2[0]:
        return False
    if b1[2] > b2[2]:
        return False
    if b1[1] < b2[1]:
        return False
    if b1[3] > b2[3]:
        return False
    return True

def merge_bbox_list(bbox_list):
    if len(bbox_list) == 0:
        pass
    bbox_res = bbox_list[0]
    for i in range(1, len(bbox_list)):
        bbox_res = merge_bbox(bbox_res, bbox_list[i])
    return BBox(bbox_res)

def merge_bbox(bbox1, bbox2):
    if isinstance(bbox1, list) or isinstance(bbox1, tuple):
        res = []
        res.append( min(bbox1[0], bbox2[0]))
        res.append( min(bbox1[1], bbox2[1]))
        res.append( max(bbox1[2], bbox2[2]))
        res.append( max(bbox1[3], bbox2[3]))
        return res
    elif isinstance(bbox1, BBox):
        return BBox([
            min(bbox1.left(), bbox2.left()),
            min(bbox1.bottom(), bbox2.bottom()),
            max(bbox1.right(), bbox2.right()),
            max(bbox1.top(), bbox2.top())
        ])
    else:
        raise Exception('unknown type of bbox')


def get_char_list_bbox(char_list, remove_accent=False):
    tmp_char_list = []
    for char in char_list:
        if not isinstance(char, LTChar):
            continue
        if remove_accent:
            from pdfxml.pdf_util.char_process import get_char_glyph
            from pdfxml.me_taxonomy.math_resources import accent_name_list
            gn = get_char_glyph(char, None)
            if gn in accent_name_list:
                continue
        tmp_char_list.append(char)

    left_list = [char.bbox[0] for char in tmp_char_list]
    right_list = [char.bbox[2] for char in tmp_char_list]
    bottom_list = [char.bbox[1] for char in tmp_char_list]
    top_list = [char.bbox[3] for char in tmp_char_list]
    if len(left_list) == 0 or\
        len(right_list) == 0 or\
        len(bottom_list) == 0 or\
        len(top_list) == 0:
        print "WARNING: no bbox for a empty char list"
        return BBox([0, 0, 0, 0])
    new_bbox = (
        np.min(left_list),
        np.min(bottom_list),
        np.max(right_list),
        np.max(top_list))
    return BBox(new_bbox)


def get_xpath_bbox(xpath):
    """
    get the left boundary of a xpath
    """
    if isinstance(xpath, LTRect) or isinstance(xpath, LTLine):
        x_list = [pt[0] for pt in xpath.pts]
        y_list = [pt[1] for pt in xpath.pts]
        min_x, max_x = np.min(x_list), np.max(x_list)
        min_y, max_y = np.min(y_list), np.max(y_list)
        return (min_x, min_y, max_x, max_y)
    else:
        raise Exception("not a line type", type(xpath))

def get_bbox_me(chars):
    """
    get the bounding box for a ME consisting of chars
    http://wiki.openstreetmap.org/wiki/Bounding_Box, (left, bottom, right, top)
    bbox of char is from bottom to top, left to right
    """
    left, bottom, right, top = chars[0].bbox
    for char in chars:
        left = min(left, char.bbox[0])
        right = max(right, char.bbox[2])
        bottom = min(bottom, char.bbox[1])
        top = max(top, char.bbox[3])
    return (left, bottom, right, top)

# xpath related function
def get_xpath_left_boundary(xpath):
    """
    get the left boundary of a xpath
    """
    if isinstance(xpath, LTRect) or isinstance(xpath, LTLine):
        #pass
        x_list = [pt[0] for pt in xpath.pts]
        min_x = np.min(x_list)
        max_x = np.max(x_list)
        return min_x
    else:
        raise Exception("not a line type")

def get_xpath_lefttop(xpath):
    """
    get the left boundary of a xpath
    """
    if isinstance(xpath, LTRect) or isinstance(xpath, LTLine):
        #pass
        x_list = [pt[0] for pt in xpath.pts]
        y_list = [pt[1] for pt in xpath.pts]
        min_x = np.min(x_list)
        max_x = np.max(x_list)
        max_y = np.max(y_list)
        return min_x, max_y
    else:
        raise Exception("not a line type")

def get_xpath_bbox(xpath):
    """
    get the left boundary of a xpath
    """
    if isinstance(xpath, LTRect) or isinstance(xpath, LTLine):
        x_list = [pt[0] for pt in xpath.pts]
        y_list = [pt[1] for pt in xpath.pts]
        min_x = np.min(x_list)
        max_x = np.max(x_list)
        min_y = np.min(y_list)
        max_y = np.max(y_list)
        return (min_x, min_y, max_x, max_y)
    else:
        raise Exception("not a line type")

def get_overlapping_xpath(chars, xpath_list):
    me_bbox = get_bbox_me(chars)
    res = []
    for xpath in xpath_list:
        if isinstance(xpath, LTRect):
            pass
        elif isinstance(xpath, LTLine):
            pass
        else:
            pass
    return res

################# deprecated ###############

# Distance statistics:
def get_median_dist():
    tmp_char_list = [c for c in chars if isinstance(c, LTChar)]
    tmp_char_list.sort(key=lambda c : c.bbox[0])
    dist_list = [ np.abs(tmp_char_list[i].bbox[0]-tmp_char_list[i+1].bbox[0]) for i in range(len(tmp_char_list)-1) ]
    print dist_list
    mv = np.median(dist_list)
    return mv
