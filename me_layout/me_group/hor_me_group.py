import xml.etree.ElementTree as ET
import pdfxml.me_layout.layout_marco as layout_marco
from pdfxml.tree import Tree
from pdfxml.pdf_util.bbox import merge_bbox_list
from pdfxml.me_layout.me_group.me_group import MEGroup, MEObject, is_basic_elem
from pdfxml.me_layout.me_group.me_group_util import skip_single_hor
from pdfxml.me_layout.char_adjust_bbox_core import can_cal_center, could_estimate_height


class MESubGroup(MEGroup):
    """
    with both supscript and subscript
    """
    def __init__(self, base_me_group, sub_me_group):
        """

        :param base_me_group: Base
        :param sub_me_group: sub part
        """
        MEGroup.__init__(self)
        MEObject.__init__(self)  # the bbox function
        self.base_me_group = base_me_group
        self.sub_me_group = sub_me_group

        self.set_adjusted_bbox(
            self.base_me_group.get_adjusted_bbox()
        )  # based on the base me group
        self.set_tight_bbox(merge_bbox_list([
            self.base_me_group.get_tight_bbox(),
            self.sub_me_group.get_tight_bbox()
        ]))

    def get_v_center(self):
        return self.base_me_group.get_v_center()

    def get_baseline_symbol(self):
        return self.base_me_group.get_baseline_symbol()

    def __str__(self):
        return "{}_{}".format(
            self.base_me_group,
            self.sub_me_group,
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MESubGroup):
            return self.base_me_group == other.base_me_group and \
                   self.sub_me_group == other.sub_me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return[self.base_me_group, self.sub_me_group]

    def attach_point_object(self):
        return self.base_me_group.attach_point_object()

    def attacher_object(self):
        # a bug before here
        return self.base_me_group.attacher_object()

    def get_cid_list(self):
        cid_list = []
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        """
        case: 28018407, with msup

        :param rn:
        :return:
        """
        n = ET.SubElement(rn, "msub")
        self.base_me_group.to_xml(n)
        self.sub_me_group.to_xml(n)

    def to_latex(self):
        return "{{{}}}_{{{}}}".format(
            self.base_me_group.to_latex(),
            self.sub_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.base_me_group.to_tree()
        t1.info['rel'] = 'HOR'
        t2 = self.sub_me_group.to_tree()
        t2.info['rel'] = 'SUB'
        t.add_children(t1)
        t.add_children(t2)
        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.base_me_group.to_triple_list())
        res_list.extend(self.sub_me_group.to_triple_list())
        base_attached_obj = self.base_me_group.attach_point_object()
        sub_attacher_obj = self.sub_me_group.attacher_object()
        assert is_basic_elem(base_attached_obj)
        assert is_basic_elem(sub_attacher_obj)
        res_list.append((sub_attacher_obj, base_attached_obj, layout_marco.REL_RSUB))
        return res_list

    def assign_id(self, i):
        self.base_me_group.assign_id(i)
        self.sub_me_group.assign_id(i)


class MESupGroup(MEGroup):
    """
    supscript only
    """
    def __init__(self, base_me_group, sup_me_group):
        """

        :param base_me_group: Base
        :param sup_me_group: sup part
        """
        MEGroup.__init__(self)
        MEObject.__init__(self)  # the bbox function
        self.base_me_group = base_me_group
        self.sup_me_group = sup_me_group
        self.set_adjusted_bbox(
            self.base_me_group.get_adjusted_bbox()
        )  # based on the base me group
        self.set_tight_bbox(merge_bbox_list([
            self.base_me_group.get_tight_bbox(),
            self.sup_me_group.get_tight_bbox()
        ]))

    def get_baseline_symbol(self):
        return self.base_me_group.get_baseline_symbol()

    def get_v_center(self):
        return self.base_me_group.get_v_center()

    def __str__(self):
        return "{}^{}".format(
            self.base_me_group,
            self.sup_me_group
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MESupGroup):
            return self.base_me_group == other.base_me_group and\
                   self.sup_me_group == other.sup_me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return [self.base_me_group, self.sup_me_group]

    def attach_point_object(self):
        return self.base_me_group.attach_point_object()

    def attacher_object(self):
        # a bug before here
        return self.base_me_group.attacher_object()

    def get_cid_list(self):
        cid_list = []
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        """
        case: 28018407, with msup

        :param rn:
        :return:
        """
        n = ET.SubElement(rn, "msup")
        self.base_me_group.to_xml(n)
        self.sup_me_group.to_xml(n)

    def to_latex(self):
        return "{{{}}}^{{{}}}".format(
            self.base_me_group.to_latex(),
            self.sup_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.base_me_group.to_tree()
        t1.info['rel'] = 'HOR'
        t2 = self.sup_me_group.to_tree()
        t2.info['rel'] = 'SUP'
        t.add_children(t1)
        t.add_children(t2)
        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.base_me_group.to_triple_list())
        res_list.extend(self.sup_me_group.to_triple_list())
        base_attached_obj = self.base_me_group.attach_point_object()
        sup_attacher_obj = self.sup_me_group.attacher_object()
        assert is_basic_elem(base_attached_obj)
        assert is_basic_elem(sup_attacher_obj)
        res_list.append((sup_attacher_obj, base_attached_obj, layout_marco.REL_RSUP))
        return res_list

    def assign_id(self, i):
        self.base_me_group.assign_id(i)
        self.sup_me_group.assign_id(i)


class MEHorGroup(MEGroup):
    """
    only horizontal relation of the elements
    """
    def __init__(self, me_groups):
        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.me_groups = me_groups

        self.set_tight_bbox(merge_bbox_list(
            [me_group.get_tight_bbox() for me_group in self.me_groups]))
        self.set_adjusted_bbox(merge_bbox_list(
            [me_group.get_adjusted_bbox() for me_group in self.me_groups]))

        # TODO: could do a checking of h overlapping? still possible over lapping

    def get_baseline_symbol(self):
        """
        prefer the one with adjustable height
        prefer the one with center height
        :return:
        """
        #raise Exception("improve and unify the function here")

        # first check whether with adjustable height
        for mg in self.me_groups:
            main_symbol = mg.get_baseline_symbol()
            if could_estimate_height(main_symbol):
                return main_symbol

        # second check whether center height
        for mg in self.me_groups:
            main_symbol = mg.get_baseline_symbol()
            if can_cal_center(main_symbol):
                return main_symbol

        # last return None
        return None

    def get_v_center(self):
        assert len(self.me_groups) > 0
        return self.me_groups[0].get_v_center()

    def __str__(self):
        res_str = "{"
        for me_group in self.me_groups:
            res_str += str(me_group)
        res_str += "}"
        return res_str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """
        test whether one equal another

        :param other:
        :return:
        """
        cur = skip_single_hor(self)
        other = skip_single_hor(other)

        if type(cur) == type(other):
            if isinstance(cur, MEHorGroup):
                for i in range(len(cur.me_groups)):
                    if cur.me_groups[i] != other.me_groups[i]:
                        return False
                return True
            else:
                return cur == other
        return False

    def children(self):
        return self.me_groups

    def attach_point_object(self):
        """
        if for semantic concern, should attach to the whole concept
        if for layout concern, better return the last one
        :return:
        """
        if len(self.me_groups) > 1:
            # NOTE, not returnning in the past...
            return self.me_groups[-1].attach_point_object()
        return self.me_groups[0].attach_point_object()

    def attacher_object(self):
        return self.me_groups[0].attacher_object()

    def get_cid_list(self):
        cid_list = []
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        """
        create a mrow for it

        :param rn:
        :return:
        """
        r_n = ET.SubElement(rn, "mrow")
        for g in self.me_groups:
            g.to_xml(r_n)

    def to_latex(self):
        return "{{{}}}".format(
            ' '.join([g.to_latex() for g in self.me_groups])
        )

    def to_tree(self):
        t = Tree()
        for mg in self.me_groups:
            tmp_t = mg.to_tree()
            tmp_t.info['rel'] = 'HOR'
            t.add_children(tmp_t)
        return t

    def to_triple_list(self):
        res_list = []
        for mg in self.me_groups:
            res_list.extend(mg.to_triple_list())
        for i in range(1, len(self.me_groups)):
            attached_obj = self.me_groups[i-1].attach_point_object()
            attacher_obj = self.me_groups[i].attacher_object()
            assert is_basic_elem(attacher_obj)
            assert is_basic_elem(attached_obj)
            res_list.append((attacher_obj, attached_obj, layout_marco.REL_HOR))
        return res_list

    def assign_id(self, i):
        for mg in self.me_groups:
            mg.assign_id(i)
