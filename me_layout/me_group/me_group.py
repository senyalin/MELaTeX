"""
The MEGroup class is in charge of layout analysis.

TODO. This module is quite adhoc now,
A better way for this module should be the 2D stochastic grammar appraoch.

TODO, re-factorize, split each function into a seperate file

The attach_point and attacher are concept from IntfyCDB
"""

import string

from pdfxml.me_taxonomy.glyph.glyph2latex import get_latex_by_glyph
from pdfxml.InftyCDB.name2latex import name2latex
from pdfxml.pdf_util.bbox import BBox
# TODO, need to export all bbox function to the class level
from pdfxml.me_layout.char_adjust_bbox_core import adjust_bbox_by_latex_val


def is_basic_elem(obj):
    is_basic = isinstance(obj, MESymbol) or isinstance(obj, MEPath) or obj is None
    if not is_basic:
        ttt = 1
    return is_basic


class MEObject(object):
    """
    This is an abstract class of all others ME object

    bbox (left, bottom, right, top)
    """
    def __init__(self, tight_bbox=None, adjusted_bbox=None):
        """
        tight_bbox is the visually measurement of the black pixels
        adjusted bbox is used to calculate the features for relative position assessment

        :param tight_bbox:
        :type tight_bbox: BBox
        :param adjusted_bbox:
        :param info:
        """
        self.tight_bbox = tight_bbox
        self.adjusted_bbox = adjusted_bbox

    def set_tight_bbox(self, bbox):
        """

        :param bbox:
        :return:
        """
        if isinstance(bbox, tuple) or isinstance(bbox, list):
            assert len(bbox) == 4
            bbox = BBox(bbox)

        assert isinstance(bbox, BBox)
        self.tight_bbox = bbox

    def get_tight_bbox(self):
        return self.tight_bbox

    def set_adjusted_bbox(self, bbox):
        if isinstance(bbox, tuple) or isinstance(bbox, list):
            bbox = BBox(bbox)
        assert isinstance(bbox, BBox)
        self.adjusted_bbox = bbox

    def get_adjusted_bbox(self):
        return self.adjusted_bbox

    def get_adjust_height(self):
        return self.adjusted_bbox.height()
        #return self.top() - self.bottom()

    def get_center(self):
        # TODO
        return self.adjusted_bbox.center()

    def get_v_center(self):
        """
        the center is the vertical center of the dominant baseline,
        for grouping of elements

        :return:
        """
        raise Exception("implement in each sub class")

    # NOTE, when checking overlapping
    # want to use the tight bbox
    # when infer the relation, use the adjusted
    # left and right does not mattter
    def left(self):
        #return self.tight_bbox.left()
        return self.adjusted_bbox.left()

    def right(self):
        return self.adjusted_bbox.right()

    def width(self):
        return self.right()-self.left()

    def tight_bottom(self):
        return self.tight_bbox.bottom()

    def adjusted_bottom(self):
        return self.adjusted_bbox.bottom()

    def tight_top(self):
        return self.tight_bbox.top()

    def adjusted_top(self):
        return self.adjusted_bbox.top()

    def v_overlap(self, me_obj):
        """

        :param me_obj: MEObj
        :type me_obj: MEObject
        :return: bool
        """
        if self.tight_top() < me_obj.tight_bottom():
            return False
        if me_obj.tight_top() < self.tight_bottom():
            return False
        return True

    def h_overlap(self, me_obj):
        """

        :param me_obj: MEObj
        :type me_obj: MEObject
        :return: bool
        """
        if self.right() < me_obj.left():
            return False
        if me_obj.right() < self.left():
            return False
        return True

    def attach_point_object(self):
        """Consistent with the InftyCDB, not in accordance with main baseline concept
        :return:
        """
        pass

    def attacher_object(self):
        """Consistent with the InftyCDB, not in accordance with main baseline concept
        """
        pass

    def get_baseline_symbol(self):
        """get the symbol on the main baseline

        If return None, means could not determine, might due to the internal groups
        :return:
        :rtype: MESymbol
        """
        raise Exception("implement in sub classes")

    def to_xml(self, rn):
        """
        abstract function

        :param rn: the root node to attach to
        :return:
        """
        raise Exception("Should not call this function, implement in the sub class")

    def to_latex(self):
        raise Exception("Should not call this function, implement in the sub class")


class MESymbol(MEObject):
    def __init__(self, latex_val, tight_bbox):
        """
        need to call the char adjustment module to adjust the bbox according to the tight bbox

        :param latex_val:
        :param tight_bbox:
        """
        super(MESymbol, self).__init__()
        self.set_tight_bbox(tight_bbox)

        # check and valid the latex value here
        if len(latex_val) == 0:
            print "meet empty latex value, invalid"
            self.latex_val = ""

        if len(latex_val) == 1:
            if latex_val in string.letters:
                self.latex_val = latex_val
            else:
                try:
                    self.latex_val = get_latex_by_glyph(latex_val)
                except:
                    print 'Met unknown single char val when init ME Symbol', latex_val
                    self.latex_val = latex_val
        else:
            # should be latex value
            if latex_val.startswith("\\"):
                self.latex_val = latex_val
            else:
                if latex_val in name2latex:
                    self.latex_val = name2latex[latex_val]
                else:
                    print "######"
                    print "could not convert for latex value", latex_val
                    self.latex_val = latex_val

        # adjust the bbox based on the latex_val and the tight_bbox
        self.set_adjusted_bbox(
            adjust_bbox_by_latex_val(tight_bbox, self.latex_val)
        )

        self.info = {}

    def get_v_center(self):
        return self.adjusted_bbox.v_center()

    def __str__(self):
        return self.latex_val

    def __repr__(self):
        return self.latex_val

    def __eq__(self, other):
        from pdfxml.path_util import ENABLE_CID_EQUQL
        #other = skip_single_hor(other)
        if isinstance(other, MESymbol):
            if ENABLE_CID_EQUQL and 'cid' in self.info:
                return self.info['cid'] == other.info['cid']
            else:
                return self.latex_val == other.latex_val
                #raise Exception("Unknown")
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_alphabetic(self):
        return len(self.latex_val) == 1 and self.latex_val in string.letters

    def set_info(self, k, v):
        self.add_info(k, v)

    def add_info(self, k, v):
        """
        add extra information for experiment purpose
        :param k:
        :param v:
        :return:
        """
        self.info[k] = v

    def get_info(self, k):
        if k in self.info:
            return self.info[k]
        return None

    def get_val(self):
        return self.latex_val

    def is_radical(self):
        return self.latex_val == "\\sqrt"

    def __str__(self):
        return str(self.latex_val)

    def attach_point_object(self):
        return self

    def attacher_object(self):
        return self

    def to_xml(self, rn):
        raise Exception("Should I do it at symbol level?")


class MEPath(MEObject):
    def __init__(self, path_bbox):
        MEObject.__init__(self)
        if isinstance(path_bbox, tuple) or isinstance(path_bbox, list):
            path_bbox = BBox(path_bbox)
        self.set_adjusted_bbox(path_bbox)
        self.set_tight_bbox(path_bbox)
        self.info = {}

    def get_v_center(self):
        return self.adjusted_bbox.v_center()

    def __eq__(self, other):
        """
        based on the assumption that there is id information
        :param other:
        :return:
        """
        if isinstance(other, MEPath):
            # only the fractional line are with cid, the radical are artifically create, so that no cid
            # only compare cid if both have
            # otherwise, compare the position.
            if 'cid' in self.info and 'cid' in other.info:
                return self.info['cid'] == other.info['cid']
            else:
                #raise Exception("Unknown situation")
                # just return true because the cid inform is missing
                # as long as both are path, should be good.
                # NOTE, TODO, might add the position checking
                left_good = self.get_tight_bbox().left() - 1 < other.get_tight_bbox().left() < self.get_tight_bbox().left()+1
                right_good = self.get_tight_bbox().right() - 1 < other.get_tight_bbox().right() < self.get_tight_bbox().right()+1
                top_good = self.get_tight_bbox().top() - 1 < other.get_tight_bbox().top() < self.get_tight_bbox().top()+1
                bottom_good = self.get_tight_bbox().bottom() - 1 < other.get_tight_bbox().bottom() < self.get_tight_bbox().bottom()+1
                return left_good and right_good and top_good and bottom_good

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_info(self, k, v):
        """
        add extra information for experiment purpose
        :param k:
        :param v:
        :return:
        """
        self.info[k] = v

    def get_info(self, k):
        if k in self.info:
            return self.info[k]
        return None

    def attach_point_object(self):
        return self

    def attacher_object(self):
        return self

    def to_xml(self, rn):
        raise Exception("Might be done in the Fraction Structure")


class MEGroup(MEObject):
    """
    abstract class for different type of MEGroup
    """
    def __init__(self):
        MEObject.__init__(self)

    def __repr__(self):
        return self.__str__()

    def is_leaf_group(self):
        return False

    def to_str_token_list(self):
        pass

    def children(self):
        """

        :return: list of MEGroup nested into it
        """
        return []

    def attach_point_object(self):
        """

        :return:
        :rtype: MEObject
        """
        raise Exception("in the sub classes")

    def attacher_object(self):
        """

        :return:
        :rtype: MEObject
        """
        raise Exception("in the sub classes")

    def to_tree(self):
        raise Exception("in the sub classes")

    def to_triple_list(self):
        raise Exception("in the sub classes")

    def assign_id(self, i):
        """
        recursively assign the id to the most basic element.

        i is the Index pointer

        :return:
        """
        raise Exception("in the sub class")