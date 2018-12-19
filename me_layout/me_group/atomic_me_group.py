import xml.etree.ElementTree as ET

from pdfxml.tree import Tree
from pdfxml.me_taxonomy.mathml.latex_encode import latex_val2mathml_encode
from pdfxml.me_layout.me_group.me_group import MEGroup, MEObject, MESymbol
from pdfxml.me_layout.me_group.me_group_util import skip_single_hor


class EmptyGroup(MEGroup):
    """
    TODO, this might be designed for the empty upper/lower bound of the binding variable
    """
    def __init__(self):
        pass

    def __str__(self):
        return ""

    def get_v_center(self):
        raise Exception("empty group don't have coordinate")

    def get_baseline_symbol(self):
        return None

    def get_cid_list(self):
        cid_list = []
        return cid_list

    def attach_point_object(self):
        return None

    def attacher_object(self):
        return None

    def to_xml(self, rn):
        """
        just do nothing

        :param rn:
        :return:
        """
        pass

    def to_latex(self):
        return ""

    def to_tree(self):
        t = Tree("")
        return t  # nothing here

    def to_triple_list(self):
        return []

    def assign_id(self, i):
        return


class MESymbolGroup(MEGroup):
    """
    keep it consistency?
    """
    def __init__(self, me_symbol):
        """

        :param me_symbol:
        :type me_symbol: MESymbol
        """
        assert isinstance(me_symbol, MESymbol)

        MEGroup.__init__(self)
        MEObject.__init__(self)
        self.me_symbol = me_symbol
        self.set_adjusted_bbox(me_symbol.get_adjusted_bbox())
        self.set_tight_bbox(me_symbol.get_tight_bbox())

    def get_v_center(self):
        return self.me_symbol.get_v_center()

    def get_baseline_symbol(self):
        return self.me_symbol

    def __str__(self):
        return str(self.me_symbol)

    def __eq__(self, other):
        other = skip_single_hor(other)
        if isinstance(other, MESymbolGroup):
            return self.me_symbol == other.me_symbol
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_info(self, k, v):
        self.me_symbol.add_info(k, v)

    def get_info(self, k):
        return self.me_symbol.get_info(k)

    def is_leaf_group(self):
        return True

    def is_radical(self):
        # NOTE: the old radical process
        return self.me_symbol.latex_val == "\\sqrt"

    def get_leaf_val(self):
        return self.me_symbol.get_val()

    def to_str_token_list(self):
        return [(str(self.me_symbol))]

    def attach_point_object(self):
        return self.me_symbol

    def attacher_object(self):
        return self.me_symbol

    def get_cid_list(self):
        cid_list = []
        cid_list.append(self.me_symbol.get_info("cid"))
        return cid_list

    def to_xml(self, rn):
        """
        op,
        rel,
        punct,
        id

        :param rn:
        :return:
        """
        from pdfxml.me_taxonomy.latex.latex_op import is_op_latex_val
        from pdfxml.me_taxonomy.latex.latex_rel import is_rel_latex_val
        from pdfxml.me_taxonomy.latex.latex_punct import is_punct_late_val
        if is_op_latex_val(self.me_symbol.latex_val) or \
                is_rel_latex_val(self.me_symbol.latex_val) or \
                is_punct_late_val(self.me_symbol.latex_val):
            n = ET.SubElement(rn, "mo")
            n.text = latex_val2mathml_encode(self.me_symbol.latex_val)
            #< mo >; < / mo >
        else:
            if self.me_symbol.latex_val.isdigit():
                n = ET.SubElement(rn, "mn")
                n.text = latex_val2mathml_encode(self.me_symbol.latex_val)
            else:
                n = ET.SubElement(rn, "mi")
                n.text = latex_val2mathml_encode(self.me_symbol.latex_val)

    def to_latex(self):
        return self.me_symbol.latex_val

    def to_tree(self):
        t = Tree("")
        t.info['rel'] = 'HOR'
        t.info['cid'] = self.get_info('cid')
        t.info['me_sym'] = self
        return t

    def to_triple_list(self):
        return []

    def assign_id(self, i):
        self.add_info('id', i.get())
        i.inc()