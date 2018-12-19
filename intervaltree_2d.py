"""
2 Dimensional Interval Tree
"""
from intervaltree import IntervalTree
from pdfxml.pdf_util.bbox import BBox


class IntervalTree2D(object):
    """

    """
    def __init__(self):
        self.name2bbox = {}
        self.hor_tree = IntervalTree()
        self.ver_tree = IntervalTree()

    def get_all_bboxes(self):
        """

        :return:
        """
        return self.name2bbox.values()

    def add_bbox(self, name, bbox):
        if isinstance(bbox, list) or isinstance(bbox, tuple):
            bbox = BBox(bbox)
        if not bbox.isvalid():
            return
        self.name2bbox[name] = bbox
        self.hor_tree.addi(bbox.left(), bbox.right(), name)
        self.ver_tree.addi(bbox.bottom(), bbox.top(), name)

    def add_bbox_only(self, bbox):

        if isinstance(bbox, list) or isinstance(bbox, tuple) or isinstance(bbox, dict):
            bbox = BBox(bbox)
        if not bbox.isvalid():
            return
        tmp_name = str(bbox)
        self.name2bbox[tmp_name] = bbox
        self.hor_tree.addi(bbox.left(), bbox.right(), tmp_name)
        self.ver_tree.addi(bbox.bottom(), bbox.top(), tmp_name)

    def get_overlap_by_name(self, name):
        the_bbox = self.name2bbox[name]
        return self.get_overlap_by_bbox(the_bbox)

    def get_overlap_by_bbox(self, the_bbox):
        if isinstance(the_bbox, list):
            the_bbox = BBox(the_bbox)
        hor_name_list = []
        i_list = self.hor_tree[the_bbox.left(): the_bbox.right()]
        #print i_list
        for interval in i_list:
            hor_name_list.append(interval.data)

        ver_name_list = []
        v_list = self.ver_tree[the_bbox.bottom(): the_bbox.top()]
        #print v_list
        for interval in v_list:
            ver_name_list.append(interval.data)

        return list(set(hor_name_list).intersection(set(ver_name_list)))

    def exist_overlap(self, the_bbox):
        """

        :param the_bbox:
        :return:
        """
        if isinstance(the_bbox, list) or isinstance(the_bbox, tuple):
            the_bbox = BBox(the_bbox)
        res_bbox_list = self.get_overlap_by_bbox(the_bbox)
        return len(res_bbox_list) > 0
