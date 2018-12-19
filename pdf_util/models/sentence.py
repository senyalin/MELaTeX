from pdfminer.layout import LTChar
from pdfxml.pdf_util.bbox import BBox
from pdfxml.pdf_util.char_process import get_latex_val_of_lt_char
from pdfxml.pdf_util.layout_util import bbox_half_overlap_list, merge_bbox_list
from pdfxml.me_extraction.separate_math_text import is_space_char
from pdfxml.me_layout.me_group.me_group import MESymbol
from pdfxml.me_layout.me_group.atomic_me_group import MESymbolGroup
from pdfxml.me_layout.me_group.internal_me_group import UnorganizedGroupPath
from pdfxml.me_layout.ugp2hgroup import ugp2hgroup


def is_sep(c):
    """
    check whether a LTChar is a separator
    None is a special rule during the processing

    :param c:
    :type c: LTChar
    :return:
    """
    if c == None:
        return True
    if is_space_char(c):
        return True
    return False


class Sentence:
    """
    This is the sentence at the human understanding level
    """
    def __init__(self):
        """
        TODO, there is a difficulty in matching the text and chars.
        some LTchars are corresponding to multiple char value, such as the (cid:xx)
        """
        # raw information
        self.text_list = []
        self.chars = []
        self.parent = None

        # derived information
        # not created during the init due to the char are added sequentially
        # marked as None for not initialized
        self.id_list_list_for_nscs = None
        self.nscs_label_list = None

    def __str__(self):
        from pdfxml.string_formatter import xw_join_string
        return xw_join_string('', self.text_list)
        #return "".join([c.encode('utf-8') for c in self.text_list])

    def set_parent(self, p):
        self.parent = p

    def get_font(self):
        if self.parent is None:
            raise Exception("should construct the hierarchy")
        return self.parent.get_font()

    #############################
    #  sentence initialization  #
    #############################
    def add_char(self, char):
        """
        char the LTChar or LTAnno
        """
        self.chars.append(char)
        self.text_list.append(char.get_text())

    def add_text(self, t):
        self.text_list.append(t)
        self.chars.append(None)

    ##########
    # sentence initialization
    ##########
    def create_nscs(self):
        """
        non separable char set
        if LTAnno or None for the char
        """
        if self.id_list_list_for_nscs is not None:
            return

        self.id_list_list_for_nscs = []

        cur_nscs_idx = []
        b = 0
        while b < len(self.chars):
            if is_sep(self.chars[b]):
                if len(cur_nscs_idx) > 0:
                    self.id_list_list_for_nscs.append(cur_nscs_idx)
                    cur_nscs_idx = []
            else:
                cur_nscs_idx.append(b)
            b += 1
        # process the last nscs
        if cur_nscs_idx:
            self.id_list_list_for_nscs.append(cur_nscs_idx)

    def get_char_nscs_list(self):
        if not self.id_list_list_for_nscs:
            self.create_nscs()
        char_nscs_list = []
        for nscs in self.id_list_list_for_nscs:
            char_nscs = [self.chars[i] for i in nscs]
            char_nscs_list.append(char_nscs)
        return char_nscs_list

    def label_nscs_eme(self, eme_bbox_list):
        sen_str = str(self)
        if sen_str.count("for some functions") > 0:
            check_point = 1
        char_nscs_list = self.get_char_nscs_list()
        if eme_bbox_list is None:
            print 'no eme bbox provided'
            return [0] * len(char_nscs_list)

        self.nscs_label_list = []
        for char_nscs in char_nscs_list:
            # check overlapping with eme_bbox
            nscs_bbox_list = [c.bbox for c in char_nscs]
            nscs_bbox = merge_bbox_list(nscs_bbox_list)

            if bbox_half_overlap_list(nscs_bbox, eme_bbox_list):
                self.nscs_label_list.append(1)
            else:
                self.nscs_label_list.append(0)
        return self.nscs_label_list

    ###########
    # export as latex for later stage of analysis
    ###########
    def export_latex(self):
        """
        export the sentence into latex format, might also need to pipeline the layout analysis

        :return:
        """
        print "Start exporting LaTeX"
        assert len(self.id_list_list_for_nscs) == len(self.nscs_label_list)
        res = ""

        nscs_id = 0  # the id for nscs
        nscs_num = len(self.id_list_list_for_nscs)

        while nscs_id < nscs_num:
            cid_list = self.id_list_list_for_nscs[nscs_id]
            nscs_str = "".join([self.text_list[cid] for cid in cid_list])
            if isinstance(nscs_str, unicode):
                nscs_str = nscs_str.encode("utf-8")

            if self.nscs_label_list[nscs_id] == 1:
                # keep finding more
                me_str = ""
                tmp_id = nscs_id

                me_symbol_groups = []  # prepare the me_symbol group for parsing

                while tmp_id < nscs_num and self.nscs_label_list[tmp_id] == 1:
                    cid_list = self.id_list_list_for_nscs[tmp_id]
                    nscs_str = "".join([self.text_list[cid] for cid in cid_list])

                    # convert from char to latex value. NOTE: there used to be a bug here.
                    for cid in cid_list:
                        latex_val = get_latex_val_of_lt_char(self.chars[cid], self.get_font())
                        # TODO, ajdust of the tight bounding box
                        bbox = BBox(self.chars[cid].bbox)

                        me_symbol_group = MESymbolGroup(MESymbol(latex_val, bbox))
                        me_symbol_groups.append(me_symbol_group)

                    if isinstance(nscs_str, unicode):
                        nscs_str = nscs_str.encode("utf-8")
                    me_str += nscs_str
                    tmp_id += 1
                nscs_id = tmp_id - 1

                # TODO, NOTE, remove the try catch to get all the parsing here

                try:
                    print "HOWDY!!!"
                    # TODO, the path is not presented here
                    ugp = UnorganizedGroupPath(me_symbol_groups, [])
                    hgroup = ugp2hgroup(ugp)
                    latex_str = hgroup.to_latex()

                    #res += "${}$ ".format(xml_str)
                    res += "${}$ ".format(latex_str)
                except Exception as e:
                    print "OH NO!!!"
                    res += "${}$ ".format(me_str)

            else:
                res += nscs_str + " "
            nscs_id += 1
        res = res.strip()
        return res

    def get_UGPs(self):
        """
        only get the UGP and test the performance of ME layout analysis
        mostly copy from the export_latex

        :return:
        """
        assert len(self.id_list_list_for_nscs) == len(self.nscs_label_list)
        ugp_list = []

        nscs_id = 0  # the id for nscs
        nscs_num = len(self.id_list_list_for_nscs)

        while nscs_id < nscs_num:
            if self.nscs_label_list[nscs_id] == 1:
                # keep finding more
                tmp_id = nscs_id

                me_symbol_groups = []  # prepare the me_symbol group for parsing

                while tmp_id < nscs_num and self.nscs_label_list[tmp_id] == 1:
                    cid_list = self.id_list_list_for_nscs[tmp_id]

                    for cid in cid_list:
                        latex_val = get_latex_val_of_lt_char(self.chars[cid], self.get_font())
                        # TODO, ajdust of the tight bounding box
                        bbox = BBox(self.chars[cid].bbox)

                        me_symbol_group = MESymbolGroup(MESymbol(latex_val, bbox))
                        me_symbol_groups.append(me_symbol_group)

                    tmp_id += 1
                nscs_id = tmp_id - 1

                # TODO, the path is not presented here
                ugp = UnorganizedGroupPath(me_symbol_groups, [])
                ugp_list.append(ugp)
            nscs_id += 1
        return ugp_list