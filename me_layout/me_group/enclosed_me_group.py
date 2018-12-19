import xml.etree.ElementTree as ET
import pdfxml.me_layout.layout_marco as layout_macro
from pdfxml.tree import Tree
from pdfxml.pdf_util.bbox import merge_bbox, merge_bbox_list
from pdfxml.me_layout.me_group.me_group import MEGroup, MEObject, MESymbol, is_basic_elem
from pdfxml.me_layout.me_group.me_group_util import skip_single_hor


class MERadicalGroup(MEGroup):
    def __init__(self, sqrt_symbol, sqrt_path, within_me_group):
        self.sqrt_symbol = sqrt_symbol
        self.sqrt_path = sqrt_path
        self.me_group = within_me_group

        self.set_adjusted_bbox(merge_bbox(
            self.sqrt_symbol.get_adjusted_bbox(),
            self.sqrt_path.get_adjusted_bbox()
        ))

        self.set_tight_bbox(self.get_adjusted_bbox())

    def get_baseline_symbol(self):
        with_in_main_symbol = self.me_group.get_baseline_symbol()
        if with_in_main_symbol is not None:
            return with_in_main_symbol
        return self.sqrt_symbol

    def get_v_center(self):
        return self.me_group.get_v_center()

    def set_me_group(self, me_group):
        self.me_group = me_group

    def __str__(self):
        return "\sqrt {}".format(self.me_group)

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MERadicalGroup):
            return self.me_group == other.me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return [self.me_group]

    def attach_point_object(self):
        return self.sqrt_symbol  # consistency with InftyCDB

    def attacher_object(self):
        return self.sqrt_symbol  # consistency with InftyCDB

    def get_cid_list(self):
        cid_list = []
        if self.sqrt_symbol.get_info("cid"):
            cid_list.append(self.sqrt_symbol.get_info("cid"))
        if self.sqrt_path.get_info("cid"):
            cid_list.append(self.sqrt_path.get_info("cid"))
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        """
        28018386
        use msqrt to enclose the inner part

        :param rn:
        :return:
        """
        n = ET.SubElement(rn, "msqrt")
        self.me_group.to_xml(n)

    def to_latex(self):
        return "\\sqrt{{{}}}".format(
            self.me_group.to_latex())

    def to_tree(self):
        t = Tree("")

        t1 = Tree("")
        t1.info['rel'] = "HOR"
        t1.info['cid'] = self.sqrt_symbol.get_info("cid")
        t1.info['me_sym'] = self.sqrt_symbol
        t2 = self.me_group.to_tree()

        t.add_children(t1)
        t.add_children(t2)

        return t

    def to_triple_list(self):
        res_list = self.me_group.to_triple_list()
        attacher_obj = self.me_group.attacher_object()
        assert is_basic_elem(attacher_obj)
        res_list.append((attacher_obj, self.sqrt_symbol, layout_macro.REL_HOR))
        return res_list

    def assign_id(self, i):
        self.sqrt_symbol.add_info('id', i.get())
        i.inc()
        self.me_group.assign_id(i)


class MEFenceGroup(MEGroup):
    """
    assumed to be generated after the sup&sub removal
    a linear of hor/sup/sub only
    """
    def __init__(self, hs_group, open_fence_symbol, close_fence_symbol=None):
        """

        :param hs_group:
        :type hs_group: me_group.internal_me_group.MEHorSupOrSubGroup
        :param open_fence_symbo:
        :type open_fence_symbo: MESymbol
        :param close_fence_symbol:
        :type close_fence_symbol: MESymbol
        """
        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.hs_group = hs_group
        self.open_fence_symbol = open_fence_symbol
        self.close_fence_symbol = close_fence_symbol

        tight_bbox_list = [
            hs_group.get_tight_bbox(),
            open_fence_symbol.get_tight_bbox(),
        ]
        if close_fence_symbol is not None:
            tight_bbox_list.append(close_fence_symbol.get_tight_bbox())
        merged_tight_bbox = merge_bbox_list(tight_bbox_list)
        self.set_tight_bbox(merged_tight_bbox)
        self.set_adjusted_bbox(hs_group.get_adjusted_bbox())

    def get_v_center(self):
        return self.open_fence_symbol.get_v_center()

    def get_baseline_symbol(self):
        main_symbol = self.hs_group.get_baseline_symbol()
        if main_symbol is not None:
            return main_symbol
        return self.open_fence_symbol

    def __str__(self):
        # TODO
        return "{}{}{}".format(
            str(self.open_fence_symbol),
            str(self.hs_group),
            str(self.close_fence_symbol)
        )

    def children(self):
        return [self.hs_group]

    def attach_point_object(self):
        return self.close_fence_symbol

    def attacher_object(self):
        return self.open_fence_symbol

    def get_cid_list(self):
        cid_list = [
            self.open_fence_symbol.get_info("cid"),
            self.close_fence_symbol.get_info("cid")
        ]
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        """
        case: 28018407

        just as mo for the parenthesis

        :param rn:
        :return:
        """
        o_n = ET.SubElement(rn, "mo")
        o_n.text = str(self.open_fence_symbol)
        self.hs_group.to_xml(rn)
        c_n = ET.SubElement(rn, "mo")
        c_n.text = str(self.close_fence_symbol)

    def to_latex(self):
        open_fence_str = str(self.open_fence_symbol)
        if open_fence_str == "{":
            open_fence_str = "\\{"
        close_fence_str = str(self.close_fence_symbol)
        if close_fence_str == '}':
            close_fence_str = "\\}"

        return "{} {} {}".format(
            open_fence_str,
            self.hs_group.to_latex(),
            close_fence_str
        )

    def to_tree(self):
        t = Tree("")

        t1 = Tree("")
        t1.info['rel'] = "HOR"
        t1.info['cid'] = self.open_fence_symbol.get_info("cid")
        t1.info['me_sym'] = self.open_fence_symbol

        t2 = self.hs_group.to_tree()

        t3 = Tree("")
        t3.info['rel'] = "HOR"
        t3.info['cid'] = self.close_fence_symbol.get_info("cid")
        t3.info['me_sym'] = self.close_fence_symbol

        t.add_children(t1)
        t.add_children(t2)
        t.add_children(t3)

        return t

    def to_triple_list(self):
        res_list = self.hs_group.to_triple_list()

        attacher_obj = self.hs_group.attacher_object()
        assert is_basic_elem(attacher_obj)

        attached_obj = self.hs_group.attach_point_object()
        assert is_basic_elem(attached_obj)

        res_list.append((attacher_obj, self.open_fence_symbol, layout_macro.REL_HOR))
        res_list.append((self.close_fence_symbol, attached_obj, layout_macro.REL_HOR))

        return res_list

    def assign_id(self, i):
        self.open_fence_symbol.add_info('id', i.get())
        i.inc()
        self.close_fence_symbol.add_info('id', i.get())
        i.inc()
        self.hs_group.assign_id(i)
