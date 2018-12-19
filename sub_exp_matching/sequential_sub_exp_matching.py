"""
Sequential sub-expression matching
"""

# TODO, the char sameness checking could be at two level
# glyph name only
# and the glyph name + the font name

from pdfxml.pdf_util.word_seg_process import char_list2char_list_list
from pdfxml.pdf_util.char_process import char_list2bbox, char_list2str
from pdfxml.sub_exp_matching.char_equal import char_same
from pdfxml.intervaltree_2d import IntervalTree2D
from pdfxml.sub_sequence import is_subsequence
from pdfxml.me_taxonomy.latex.latex_punct import latex_punct_list


class SubExpMatching(object):
    def __init__(self, pid2me_char_list_list):
        self.pid2me_char_list_list = pid2me_char_list_list
        self.pid2it2d = {}
        for pid, me_char_list_list in pid2me_char_list_list.items():
            it2d = IntervalTree2D()
            for char_list in me_char_list_list:
                it2d.add_bbox_only(char_list2bbox(char_list))
            self.pid2it2d[pid] = it2d

    def is_new_matching(self, nscs, pid):
        """
        the new here means it's not recognized earlier

        The matching here only concern with the char value
        Should not overlapping with an existing me

        :param nscs: list of LTChar sorted by the left bound
        :return:
        """
        # skip the punct

        s = char_list2str(nscs)
        ignore_single_char_list = ['(', ')', '[', ']', '{', '}', 'a', 'A']
        if s.strip() in latex_punct_list or s in ignore_single_char_list:
            # a and A are the only possible sequence to be matched out
            return False

        nscs_bbox = char_list2bbox(nscs)
        if self.pid2it2d[pid].exist_overlap(nscs_bbox):
            return False
        print("It's very inefficient now")
        for me_nscs in self.pid2me_char_list_list[pid]:
            if is_subsequence(nscs, me_nscs, char_same):
                return True
        return False


def sequential_sub_matching(lines, sem, pid):
    """

    :param lines:
    :param sem: sem is short for SubExpMatching
    :return:
        return a list of char_list for the new matched me
        that does not overlap with existing matched MEs.
    """
    nscs_me_list = []
    for line in lines:
        nscs_list = char_list2char_list_list(line)
        for nscs in nscs_list:
            if sem.is_new_matching(nscs, pid):
                nscs_me_list.append(nscs)
    return nscs_me_list
