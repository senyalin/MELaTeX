import xml.etree.ElementTree as ET
import pdfxml.me_layout.layout_marco as layout_marco
from pdfxml.tree import Tree
from pdfxml.me_taxonomy.mathml.latex_encode import latex_val2mathml_encode
from pdfxml.pdf_util.bbox import merge_bbox_list, merge_bbox
from pdfxml.me_layout.me_group.me_group import MEGroup, MEObject, MESymbol, is_basic_elem
from pdfxml.me_layout.me_group.atomic_me_group import EmptyGroup, MESymbolGroup
from pdfxml.me_layout.me_group.me_group_util import skip_single_hor


class GridGroup(MEGroup):
    def __init__(self, mg_mat):
        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.mg_mat = mg_mat

        # tight bbox
        tmp_mg_list = []
        for r, mg_list in enumerate(self.mg_mat):
            for c, mg in enumerate(mg_list):
                tmp_mg_list.append(mg)
        merged_bbox = merge_bbox_list([mg.get_tight_bbox() for mg in tmp_mg_list])
        self.set_tight_bbox(merged_bbox)

        # TODO, adjust bbox
        self.set_adjusted_bbox(merged_bbox)


    def get_baseline_symbol(self):
        return self.mg_mat[0][0].get_baseline_symbol()

    def get_v_center(self):
        return self.get_tight_bbox().get_v_center()

    def children(self):
        tmp_mg_list = []
        for r, mg_list in enumerate(self.mg_mat):
            for c, mg in enumerate(tmp_mg_list):
                tmp_mg_list.append(mg)
        return tmp_mg_list

    def __str__(self):
        content = "Grid MG\n"
        for r, mg_list in enumerate(self.mg_mat):
            content += "Grid Row\n"
            for c, mg in enumerate(mg_list):
                content += str(mg)
        return content

    def __eq__(self, other):
        if not isinstance(other, GridGroup):
            return False
        if len(self.mg_mat) != len(other.mg_mat):
            return False
        for r in range(len(self.mg_mat)):
            if len(self.mg_mat[r]) != len(other.mg_mat[r]):
                return False
            for c in range(len(self.mg_mat[r])):
                if self.mg_mat[r][c] != other.mg_mat[r][c]:
                    return False
        return True

    def attach_point_object(self):
        return self.mg_mat[0][0].attach_point_object()

    def attacher_object(self):
        return self.mg_mat[-1][-1].attach_point_object()

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
        raise Exception("TODO Grid")

    def to_latex(self):
        raise Exception("TODO Grid")

    def to_tree(self):
        """
        for the InftyCDB compairson

        :return:
        """
        raise Exception("TODO Grid")

    def to_triple_list(self):
        """
        for InftyCDB

        :return:
        """
        raise Exception("TODO Grid")

    def assign_id(self, i):
        """
        not sure what this is for
        :param i:
        :return:
        """
        raise Exception("TODO Grid")


class MESupSubGroup(MEGroup):
    """
    with both supscript and subscript
    """
    def __init__(self, base_me_group, sup_me_group, sub_me_group):
        """

        :param base_me_group: Base
        :param sup_me_group: sup part
        :param sub_me_group: sub part
        """
        MEGroup.__init__(self)
        MEObject.__init__(self)  # the bbox function
        self.base_me_group = base_me_group
        self.sup_me_group = sup_me_group
        self.sub_me_group = sub_me_group

        self.set_adjusted_bbox(
            self.base_me_group.get_adjusted_bbox()
        )  # based on the base me group
        self.set_tight_bbox(merge_bbox_list([
            self.base_me_group.get_tight_bbox(),
            self.sup_me_group.get_tight_bbox(),
            self.sub_me_group.get_tight_bbox()
        ]))

    def get_baseline_symbol(self):
        return self.base_me_group.get_baseline_symbol()

    def get_v_center(self):
        return self.base_me_group.get_v_center()

    def children(self):
        return [self.base_me_group, self.sub_me_group, self.sup_me_group]

    def __str__(self):
        return "{{{}}}_{{{}}}^{{{}}}".format(
            self.base_me_group,
            self.sub_me_group,
            self.sup_me_group
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MESupSubGroup):
            return self.base_me_group == other.base_me_group \
                   and self.sup_me_group == other.sup_me_group \
                   and self.sub_me_group == other.sub_me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def attach_point_object(self):
        return self.base_me_group.attach_point_object()

    def attacher_object(self):
        return self.base_me_group.attach_point_object()

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
        n = ET.SubElement(rn, "msubsup")
        self.base_me_group.to_xml(n)
        self.sub_me_group.to_xml(n)
        self.sup_me_group.to_xml(n)

    def to_latex(self):
        return "{{{}}}_{{{}}}^{{{}}}".format(
            self.base_me_group.to_latex(),
            self.sub_me_group.to_latex(),
            self.sup_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.base_me_group.to_tree()
        t1.info['rel'] = 'HOR'
        t.add_children(t1)
        t2 = self.sup_me_group.to_tree()
        t2.info['rel'] = 'SUP'
        t.add_children(t2)
        t3 = self.sub_me_group.to_tree()
        t3.info['rel'] = 'SUB'
        t.add_children(t3)
        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.base_me_group.to_triple_list())
        res_list.extend(self.sub_me_group.to_triple_list())
        res_list.extend(self.sup_me_group.to_triple_list())
        attached_obj = self.base_me_group.attach_point_object()
        sub_attacher_obj = self.sub_me_group.attacher_object()
        sup_attacher_obj = self.sup_me_group.attacher_object()
        assert is_basic_elem(attached_obj)
        assert is_basic_elem(sub_attacher_obj)
        assert is_basic_elem(sup_attacher_obj)
        res_list.append((sub_attacher_obj, attached_obj, layout_marco.REL_RSUB))
        res_list.append((sup_attacher_obj, attached_obj, layout_marco.REL_RSUP))
        return res_list

    def assign_id(self, i):
        self.base_me_group.assign_id(i)
        self.sup_me_group.assign_id(i)
        self.sub_me_group.assign_id(i)


class MEUpperUnderGroup(MEGroup):
    def __init__(self, base_me_group, upper_me_group, under_me_group):
        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.base_me_group = base_me_group
        self.upper_me_group = upper_me_group
        self.under_me_group = under_me_group
        self.set_adjusted_bbox(self.base_me_group.get_adjusted_bbox())
        self.set_tight_bbox(merge_bbox_list([
            self.base_me_group.get_tight_bbox(),
            self.upper_me_group.get_tight_bbox(),
            self.under_me_group.get_tight_bbox()
        ]))

    def get_baseline_symbol(self):
        return self.base_me_group.get_baseline_symbol()

    def get_v_center(self):
        return self.base_me_group.get_v_center()

    def __str__(self):
        return "\\overunder {{{}}} {{{}}} {{{}}}".format(
            self.base_me_group,
            self.upper_me_group,
            self.under_me_group
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MEUpperUnderGroup):
            return self.base_me_group == other.base_me_group \
                   and self.upper_me_group == other.upper_me_group \
                   and self.under_me_group == other.under_me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return [self.base_me_group, self.upper_me_group, self.under_me_group]

    def attacher_object(self):
        return self.base_me_group.attacher_object()

    def attach_point_object(self):
        return self.base_me_group.attach_point_object()

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
        n = ET.SubElement(rn, "munderover")
        self.base_me_group.to_xml(n)
        self.under_me_group.to_xml(n)
        self.upper_me_group.to_xml(n)

    def to_latex(self):
        """
        https://stackoverflow.com/questions/3098680/how-to-put-a-symbol-above-another-in-latex

        :return:
        """
        return "\\overset{{{}}}{{ \\underset{{{}}} {{{}}} }}".format(
            self.upper_me_group.to_latex(),
            self.under_me_group.to_latex(),
            self.base_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.base_me_group.to_tree()
        t1.info['rel'] = 'HOR'
        t.add_children(t1)
        t2 = self.upper_me_group.to_tree()
        t2.info['rel'] = 'UPPER'
        t.add_children(t2)
        t3 = self.under_me_group.to_Tree()
        t3.info['rel'] = 'UNDER'
        t.add_children(t3)
        return t

    def to_triple_list(self):
        """

        :return:
        """
        res_list = []
        res_list.extend(self.base_me_group.to_triple_list())
        res_list.extend(self.upper_me_group.to_triple_list())
        res_list.extend(self.under_me_group.to_triple_list())
        attached_obj = self.base_me_group.attach_point_object()
        upper_attacher_obj = self.upper_me_group.attacher_object()
        under_attacher_obj = self.under_me_group.attacher_object()
        assert is_basic_elem(attached_obj)
        assert is_basic_elem(upper_attacher_obj)
        assert is_basic_elem(under_attacher_obj)
        res_list.append((upper_attacher_obj, attached_obj, layout_marco.REL_UPPER))
        res_list.append((under_attacher_obj, attached_obj, layout_marco.REL_UNDER))
        return res_list

    def assign_id(self, i):
        self.base_me_group.assign_id(i)
        self.upper_me_group.assign_id(i)
        self.under_me_group.assign_id(i)


class MEBindVarGroup(MEGroup):
    """
    NOTE that the bind var is a semantical concept,
    At the layout level, this is referring to a type of vertical structure that have under and upper parts.

    """
    def __init__(self, bind_var_symbol, up_me_group, down_me_group):
        """

        :param bind_var_symbol:
        :type bind_var_symbol: MESymbolGroup
        :param up_me_group:
        :type up_me_group: MEGroup
        :param down_me_group:
        :type down_me_group: MEGroup
        """
        MEGroup.__init__(self)
        MEObject.__init__(self)

        self.bind_var_symbol = bind_var_symbol
        if up_me_group is None:
            self.up_me_group = EmptyGroup()
        else:
            self.up_me_group = up_me_group
        if down_me_group is None:
            self.down_me_group = EmptyGroup()
        else:
            self.down_me_group = down_me_group

        tight_bbox = bind_var_symbol.get_tight_bbox()
        if not isinstance(up_me_group, EmptyGroup):
            # TODO, NOTE, commented out, the assertion might be related with the layout analysis sequence
            # might only for debugging purpose
            #assert isinstance(up_me_group, UnorganizedGroupPath)
            if len(up_me_group.me_groups) != 0:
                tight_bbox = merge_bbox(tight_bbox, up_me_group.get_tight_bbox())

        if not isinstance(down_me_group, EmptyGroup):
            # TODO, NOTE, commented out, the assertion might be related with the layout analysis sequence
            # might only for debugging purpose
            #assert isinstance(down_me_group, UnorganizedGroupPath)
            if len(down_me_group.me_groups) != 0:
                tight_bbox = merge_bbox(tight_bbox, down_me_group.get_tight_bbox())
        self.set_tight_bbox(tight_bbox)

        self.set_adjusted_bbox(
            self.bind_var_symbol.get_adjusted_bbox())

    def get_baseline_symbol(self):
        if isinstance(self.bind_var_symbol, MESymbol):
            return self.bind_var_symbol
        elif isinstance(self.bind_var_symbol, MESymbolGroup):
            return self.bind_var_symbol.me_symbol
        else:
            raise Exception("unknown type for the bind symbol")

    def get_v_center(self):
        return self.bind_var_symbol.get_v_center()

    def __str__(self):
        return "{}_{}^{}".format(
            self.bind_var_symbol,
            self.down_me_group,
            self.up_me_group
        )

    def children(self):
        return [self.down_me_group, self.up_me_group]

    def attach_point_object(self):

        return self.bind_var_symbol.me_symbol

    def attacher_object(self):
        return self.bind_var_symbol.me_symbol

    def get_cid_list(self):
        cid_list = [self.bind_var_symbol.get_info("cid")]
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        """
        case: 28018407, with msup

        :param rn:
        :return:
        """
        if isinstance(self.up_me_group, EmptyGroup):
            n = ET.SubElement(rn, "munder")
            o_n = ET.SubElement(n, "mo")
            o_n.text = latex_val2mathml_encode(str(self.bind_var_symbol))
            self.down_me_group.to_xml(n)
        else:
            # TODO, it's possible the upper part is empty, in this case, will reduce to munder
            n = ET.SubElement(rn, "munderover")
            o_n = ET.SubElement(n, "mo")
            o_n.text = latex_val2mathml_encode(str(self.bind_var_symbol))
            self.down_me_group.to_xml(n)
            self.up_me_group.to_xml(n)

    def to_latex(self):
        return "{}_{{{}}}^{{{}}}".format(
            str(self.bind_var_symbol),
            self.down_me_group.to_latex(),
            self.up_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.bind_var_symbol.to_tree()
        t1.info['rel'] = 'HOR'
        t.add_children(t1)
        t2 = self.up_me_group.to_tree()
        t2.info['rel'] = 'BIND_UPPER'
        t.add_children(t2)
        t3 = self.down_me_group.to_tree()
        t3.info['rel'] = 'BIND_UNDER'
        t.add_children(t3)
        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.up_me_group.to_triple_list())
        res_list.extend(self.down_me_group.to_triple_list())
        up_attacher_obj = self.up_me_group.attacher_object()
        down_attacher_obj = self.down_me_group.attacher_object()
        assert is_basic_elem(up_attacher_obj)
        assert is_basic_elem(down_attacher_obj)
        res_list.append((up_attacher_obj, self.bind_var_symbol, layout_marco.REL_UPPER))
        res_list.append((down_attacher_obj, self.bind_var_symbol, layout_marco.REL_UNDER))
        return res_list

    def assign_id(self, i):
        self.bind_var_symbol.me_symbol.add_info('id', i.get())
        i.inc()
        self.up_me_group.assign_id(i)
        self.down_me_group.assign_id(i)


class MEUpperGroup(MEGroup):
    def __init__(self, base_me_group, upper_me_group):
        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.base_me_group = base_me_group
        self.upper_me_group = upper_me_group
        self.set_adjusted_bbox(self.base_me_group.get_adjusted_bbox())
        self.set_tight_bbox(merge_bbox_list([
            self.base_me_group.get_tight_bbox(),
            self.upper_me_group.get_tight_bbox()
        ]))

    def get_baseline_symbol(self):
        """
        not sure about
        :return:
        """
        return self.base_me_group.get_baseline_symbol()

    def get_v_center(self):
        return self.base_me_group.get_v_center()

    def __str__(self):
        return "\\overset{{{}}}{{{}}}".format(
            self.base_me_group,
            self.upper_me_group
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MEUpperGroup):
            return self.base_me_group == other.base_me_group \
                   and self.upper_me_group == other.upper_me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return [self.base_me_group, self.upper_me_group]

    def attach_point_object(self):
        return self.base_me_group.attach_point_object()

    def attacher_object(self):
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
        n = ET.SubElement(rn, "mover")
        self.base_me_group.to_xml(n)
        self.upper_me_group.to_xml(n)

    def to_latex(self):
        return "\\overset{{{}}}{{{}}}".format(
            self.upper_me_group.to_latex(),
            self.base_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.base_me_group.to_tree()
        t1.info['rel'] = 'HOR'
        t.add_children(t1)
        t2 = self.upper_me_group.to_tree()
        t2.info['rel'] = 'UPPER'
        t.add_children(t2)
        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.base_me_group.to_triple_list())
        res_list.extend(self.upper_me_group.to_triple_list())
        attached_obj = self.base_me_group.attach_point_object()
        upper_attacher_obj = self.upper_me_group.attacher_object()
        assert is_basic_elem(attached_obj)
        assert is_basic_elem(upper_attacher_obj)
        res_list.append((upper_attacher_obj, attached_obj, layout_marco.REL_UPPER))
        return res_list

    def assign_id(self, i):
        self.base_me_group.assign_id(i)
        self.upper_me_group.assign_id(i)


class MEUnderGroup(MEGroup):
    def __init__(self, base_me_group, under_me_group):
        """

        :param base_me_group:
        :param under_me_group:
        """
        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.base_me_group = base_me_group
        self.under_me_group = under_me_group
        # the adjusted is to calculate the relative relationship between groups
        self.set_adjusted_bbox(self.base_me_group.get_adjusted_bbox())
        # the tight bbox is for the assessment of the relationship of overlapping
        self.set_tight_bbox(merge_bbox_list([
            self.base_me_group.get_tight_bbox(),
            self.under_me_group.get_tight_bbox()
        ]))

    def get_baseline_symbol(self):
        """
        not sure about
        :return:
        """
        return self.base_me_group.get_baseline_symbol()

    def get_v_center(self):
        return self.base_me_group.get_v_center()

    def __str__(self):
        return "\\underset{{{}}}{{{}}}".format(
            self.base_me_group,
            self.under_me_group
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MEUnderGroup):
            return self.base_me_group == other.base_me_group and \
                   self.under_me_group == other.under_me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return [self.base_me_group, self.under_me_group]

    def attach_point_object(self):
        return self.base_me_group.attach_point_object()

    def attacher_object(self):
        return self.base_me_group.attacher_object()

    def get_cid_list(self):
        cid_list = []
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        """
        case: 28018407, with msup
        https://www.w3.org/TR/REC-MathML/chap3_4.html#sec3.4.6

        :param rn:
        :return:
        """
        n = ET.SubElement(rn, "mover")
        self.base_me_group.to_xml(n)
        self.under_me_group.to_xml(n)

    def to_latex(self):
        return "\\underset{{{}}}{{{}}}".format(
            self.under_me_group.to_latex(),
            self.base_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.base_me_group.to_tree()
        t1.info['rel'] = 'HOR'
        t.add_children(t1)
        t2 = self.under_me_group.to_tree()
        t2.info['rel'] = 'UNDER'
        t.add_children(t2)
        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.base_me_group.to_triple_list())
        res_list.extend(self.under_me_group.to_triple_list())
        attached_obj = self.base_me_group.attach_point_object()
        under_attacher_obj = self.under_me_group.attacher_object()
        assert is_basic_elem(attached_obj)
        assert is_basic_elem(under_attacher_obj)
        res_list.append((under_attacher_obj, attached_obj, layout_marco.REL_UNDER))
        return res_list

    def assign_id(self, i):
        self.base_me_group.assign_id(i)
        self.under_me_group.assign_id(i)


class MEFractionGroup(MEGroup):
    def __init__(self, fraction_path, up_me_group, down_me_group):
        self.frac_path = fraction_path
        self.up_me_group = up_me_group
        self.down_me_group = down_me_group

        # update the bbox of this Fraction group
        self.set_tight_bbox(merge_bbox(
            self.up_me_group.get_tight_bbox(),
            self.down_me_group.get_tight_bbox(),
        ))
        self.set_adjusted_bbox(merge_bbox(
            self.up_me_group.get_adjusted_bbox(),
            self.down_me_group.get_adjusted_bbox(),
        ))

    def get_baseline_symbol(self):
        """
        not sure about
        :return:
        """
        return MESymbol("/", self.frac_path.get_tight_bbox())

    def get_v_center(self):
        return self.frac_path.get_v_center()

    def __str__(self):
        return "\\frac{{{}}}{{{}}}".format(
            self.up_me_group,
            self.down_me_group
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MEFractionGroup):
            return self.up_me_group == other.up_me_group and self.down_me_group == other.down_me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return [self.up_me_group, self.down_me_group]

    def attach_point_object(self):
        return self.frac_path  # consistency with InftyCDB

    def attacher_object(self):
        return self.frac_path  # consistency with InftyCDB

    def get_cid_list(self):
        cid_list = [self.frac_path.get_info("cid")]
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        n = ET.SubElement(rn, 'mfrac')
        self.up_me_group.to_xml(n)
        self.down_me_group.to_xml(n)

    def to_latex(self):
        return "\\frac{{{}}}{{{}}}".format(
            self.up_me_group.to_latex(),
            self.down_me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()
        t1 = self.up_me_group.to_tree()
        t1.info['rel'] = 'FRAC_UP'
        t.add_children(t1)
        t2 = self.down_me_group.to_tree()
        t2.info['rel'] = 'FRAC_DOWN'
        t.add_children(t2)
        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.up_me_group.to_triple_list())
        res_list.extend(self.down_me_group.to_triple_list())
        up_attacher_obj = self.up_me_group.attacher_object()
        down_attacher_obj = self.down_me_group.attacher_object()
        assert is_basic_elem(up_attacher_obj)
        assert is_basic_elem(down_attacher_obj)
        res_list.append((up_attacher_obj, self.frac_path, layout_marco.REL_UPPER))
        res_list.append((down_attacher_obj, self.frac_path, layout_marco.REL_UNDER))
        return res_list

    def assign_id(self, i):
        self.frac_path.add_info('id', i.get())
        i.inc()
        self.up_me_group.assign_id(i)
        self.down_me_group.assign_id(i)


class MEAccentGroup(MEGroup):
    def __init__(self, hat_symbol, me_group):
        """

        :param hat_symbol:
        :type hat_symbol: MESymbol
        :param me_group:
        :type me_group: MEGroup
        """
        assert isinstance(hat_symbol, MESymbol)
        self.accent_symbol = hat_symbol
        self.me_group = me_group
        if isinstance(me_group, EmptyGroup):
            self.set_tight_bbox(self.accent_symbol.get_tight_bbox())
            self.set_adjusted_bbox(
                self.accent_symbol.get_adjusted_bbox()
            )
        else:
            self.set_tight_bbox(merge_bbox(
                self.accent_symbol.get_tight_bbox(),
                self.me_group.get_tight_bbox()
            ))
            self.set_adjusted_bbox(
                self.me_group.get_adjusted_bbox()
            )

    def get_baseline_symbol(self):
        return self.me_group.get_baseline_symbol()

    def get_v_center(self):
        return self.me_group.get_v_center()

    def __str__(self):
        return "\\{} {}".format(
            self.accent_symbol,
            self.me_group
        )

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MEAccentGroup):
            return self.me_group == other.me_group
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def children(self):
        return [self.me_group]

    def attach_point_object(self):
        return self.accent_symbol  # consistency with InftyCDB

    def attacher_object(self):
        return self.accent_symbol  # consistency with InftyCDB

    def get_cid_list(self):
        cid_list = []
        cid_list.append(self.accent_symbol.get_info("cid"))
        for g in self.children():
            cid_list.extend(g.get_cid_list())
        return cid_list

    def to_xml(self, rn):
        from pdfxml.me_taxonomy.math_resources import under_name_list
        if str(self.accent_symbol) in under_name_list:
            n = ET.SubElement(rn, "munder")
            n.set("accent", "true")
            self.me_group.to_xml(n)
            accent_n = ET.SubElement(n, "mo")
            accent_n.text = latex_val2mathml_encode(str(self.accent_symbol))
        else:
            n = ET.SubElement(rn, "mover")
            n.set("accent", "true")
            self.me_group.to_xml(n)
            accent_n = ET.SubElement(n, "mo")
            accent_n.text = latex_val2mathml_encode(str(self.accent_symbol))

    def to_latex(self):
        return "{} {{{}}}".format(
            str(self.accent_symbol),
            self.me_group.to_latex()
        )

    def to_tree(self):
        t = Tree()

        t1 = self.me_group.to_tree()
        t1.info['rel'] = 'HOR'
        t.add_children(t1)

        t2 = Tree()
        t2.info['cid'] = self.accent_symbol.get_info('cid')
        t2.info['me_sym'] = self.accent_symbol
        from pdfxml.me_taxonomy.math_resources import under_name_list
        if str(self.accent_symbol) in under_name_list:
            t2.info['rel'] = 'ACCENT_DOWN'
        else:
            t2.info['rel'] = 'ACCENT_UP'
        t.add_children(t2)

        return t

    def to_triple_list(self):
        res_list = []
        res_list.extend(self.me_group.to_triple_list())
        attacher_obj = self.me_group.attacher_object()
        assert is_basic_elem(attacher_obj)
        from pdfxml.me_taxonomy.math_resources import under_name_list
        if str(self.accent_symbol) in under_name_list:
            res_list.append((self.accent_symbol, attacher_obj, layout_marco.REL_UNDER))
        else:
            res_list.append((self.accent_symbol, attacher_obj, layout_marco.REL_UPPER))
        return res_list

    def assign_id(self, i):
        self.accent_symbol.add_info('id', i.get())
        i.inc()
        self.me_group.assign_id(i)
