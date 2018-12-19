from pdfxml.loggers import me_parsing_logger
from pdfxml.me_layout.me_group.atomic_me_group import MESymbolGroup
from pdfxml.pdf_util.bbox import merge_bbox_list
from pdfxml.me_layout.me_group.me_group import MEGroup, MEObject


class UnorganizedGroupPath(MEGroup):
    """
    could not handle the puncutation well?

    """
    def __init__(self, me_groups, me_paths, remove_ime=False):
        self.me_groups = me_groups
        self.me_paths = me_paths
        self.me_groups.sort(key=lambda mg:mg.get_tight_bbox().left())
        if remove_ime:
            self.remove_ime_notation()
        # adjust_tight_bbox by path
        self.adjust_me_group_bbox_by_path()
        self.adjust_me_group_bbox_overlapping()

        tight_bboxes = [me_group.get_tight_bbox() for me_group in self.me_groups]
        tight_bboxes.extend([me_path.get_tight_bbox() for me_path in self.me_paths])
        if len(tight_bboxes) == 0:
            raise Exception("empty bboxes")

        self.set_tight_bbox(merge_bbox_list(tight_bboxes))

        adjusted_bboxes = [me_group.get_adjusted_bbox() for me_group in self.me_groups]
        adjusted_bboxes.extend([me_path.get_adjusted_bbox() for me_path in self.me_paths])
        self.set_adjusted_bbox(merge_bbox_list(adjusted_bboxes))

    def get_baseline_symbol(self):
        return None

    def get_v_center(self):
        raise Exception("ugp don't have the center")

    def remove_ime_notation(self):
        """
        remove the last punctuation and the parenthesis denoting the equation number

        :return:
        """
        matched_eq_num = False
        i = len(self.me_groups)-1
        if isinstance(self.me_groups[i], MESymbolGroup):
            if self.me_groups[i].me_symbol.latex_val == ')':
                i -= 1
                while i >= 0:
                    if isinstance(self.me_groups[i], MESymbolGroup):
                        if self.me_groups[i].me_symbol.latex_val in "0123456789abc":
                            i -= 1
                        else:
                            break
                    else:
                        break
                if i >= 0:
                    if isinstance(self.me_groups[i], MESymbolGroup):
                        if self.me_groups[i].me_symbol.latex_val == '(':
                            matched_eq_num = True
        last_idx = len(self.me_groups)-1
        if matched_eq_num:
            last_idx = i-1
        if last_idx >= 0:
            if isinstance(self.me_groups[last_idx], MESymbolGroup):
                if self.me_groups[last_idx].me_symbol.latex_val in ',.':
                    last_idx -= 1
        self.me_groups = self.me_groups[:last_idx+1]

    def adjust_me_group_bbox_overlapping(self):
        """
        if the bounding box intersect
        just for a few, such as \\sum, \\prod, \\hat
        :return:
        """

        # TODO, much harder for the accent
        from pdfxml.me_taxonomy.math_resources import accent_name_list

        tmp_big_op_list = ['\\sum', '\\prod']
        for i, me_group in enumerate(self.me_groups):
            cur_mg = me_group
            cur_bbox = cur_mg.get_tight_bbox()
            if isinstance(me_group, MESymbolGroup):
                latex_val = me_group.me_symbol.latex_val
                if latex_val in tmp_big_op_list:
                    # check for all intersections
                    new_upper, new_under = \
                        me_group.get_tight_bbox().top(), \
                        me_group.get_tight_bbox().bottom()
                    for j, tmp_mg in enumerate(self.me_groups):
                        if i == j:
                            continue
                        tmp_bbox = tmp_mg.get_tight_bbox()
                        if cur_bbox.overlap(tmp_bbox):
                            cur_v_center = cur_bbox.v_center()
                            if tmp_bbox.bottom() > cur_v_center:
                                new_upper = min(new_upper, tmp_bbox.bottom())
                            elif tmp_bbox.top() < cur_v_center:
                                new_under = max(new_under, tmp_bbox.top())
                            else:
                                raise Exception("The other bbox should not overlap the center")
                    new_bbox = [
                        cur_bbox.left(), new_under,
                        cur_bbox.right(), new_upper]
                    me_parsing_logger.debug("Set new bbox as {}".format(new_bbox))
                    cur_mg.set_tight_bbox(new_bbox)

    def adjust_me_group_bbox_by_path(self):
        """
        if the me_group is crossed by the path
        adjust by the larger part after split
        :return:
        """
        for i, me_group in enumerate(self.me_groups):
            me_bbox = me_group.get_tight_bbox()
            for path in self.me_paths:
                path_bbox = path.get_tight_bbox()
                if me_bbox.h_overlap(path_bbox) and me_bbox.v_overlap(path_bbox):
                    path_bbox_v_center = path_bbox.v_center()
                    path_bbox_height = path_bbox.height()
                    bbox1, bbox2 = me_bbox.v_split(path_bbox_v_center, path_bbox_height*1.1/2)
                    if bbox1.area() > bbox2.area():
                        me_parsing_logger.debug("ADJUST BBox by Path {} to {}".format(
                            me_bbox, bbox1
                        ))
                        me_group.set_tight_bbox(bbox1)
                    else:
                        me_parsing_logger.debug("ADJUST BBox by Path {} to {}".format(
                            me_bbox, bbox2
                        ))
                        me_group.set_tight_bbox(bbox2)

    def children(self):
        return self.me_groups

    def set_me_groups(self, me_groups):
        self.me_groups = me_groups

    def set_me_paths(self, me_paths):
        self.me_paths = me_paths

    def __str__(self):
        res_str = ""
        for me_group in self.me_groups:
            res_str += str(me_group)
        return res_str

    def attach_point_object(self):
        raise Exception("no attach for UGP")

    def attacher_object(self):
        raise Exception("no attach for UGP")

    def get_cid_list(self):
        cid_list = []
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list


class MEHSSGroup(MEGroup):
    """
    The relative position between me_group
    in me_groups could only be Hor/ Sub/ Sup
    """
    def __init__(self, me_groups):
        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.me_groups = me_groups
        self.set_tight_bbox(merge_bbox_list(
            [me_group.get_tight_bbox() for me_group in self.me_groups]))
        self.set_adjusted_bbox(merge_bbox_list(
            [me_group.get_adjusted_bbox() for me_group in self.me_groups]))

    def get_baseline_symbol(self):
        return self.me_groups[0].get_baseline_symbol()

    def get_v_center(self):
        return self.me_groups[0].get_v_center()

    def __str__(self):
        res_str = ""
        for me_group in self.me_groups:
            res_str += str(me_group)
        return res_str

    def children(self):
        return self.me_groups

    def attach_point_object(self):
        raise Exception("HSS internal MEGroup")

    def attacher_object(self):
        raise Exception("HSS internal MEGroup")

    def get_cid_list(self):
        cid_list = []
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list


class MEHorSupOrSubGroup(MEGroup):
    """
    will not have sup and sub at the same time
    """
    def __init__(self, me_groups):
        MEGroup.__init__(self)
        MEObject.__init__(self)

        if len(me_groups) == 0:
            pass

        self.me_groups = me_groups
        self.set_tight_bbox(merge_bbox_list(
            [me_group.get_tight_bbox() for me_group in self.me_groups]))
        self.set_adjusted_bbox(merge_bbox_list(
            [me_group.get_adjusted_bbox() for me_group in self.me_groups]))
        # TODO: could do a checking of h overlapping? still possible over lapping

    def get_baseline_symbol(self):
        return self.me_groups[0].get_baseline_symbol()

    def get_v_center(self):
        return self.me_groups[0].get_v_center()

    def __str__(self):
        res_str = ""
        for me_group in self.me_groups:
            res_str += str(me_group)
        return res_str

    def children(self):
        return self.me_groups

    def attach_point_object(self):
        raise Exception("HSS internal MEGroup")

    def attacher_object(self):
        raise Exception("HSS internal MEGroup")

    def get_cid_list(self):
        cid_list = []
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list