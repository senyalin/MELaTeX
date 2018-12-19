from xml.etree import ElementTree as ET
from pdfxml.pdf_util.models.block import Block
from pdfxml.pdf_util.models.sentence import Sentence
from pdfxml.pdf_util.layout_util import bbox_half_overlap_list


class ParagraphBlock(Block):
    def __init__(self, llines, eme_bbox_list):
        """
        the eme_bbox_list is obtained from the page level

        :param llines:
        :type llines: list[LayoutLine]
        :param eme_bbox_list: bbox of the EME
        :type eme_bbox_list: list[tuple]
        :return:
        """
        self.parent = None  # the parent should be section

        # raw data
        Block.__init__(self)
        self.eme_bbox_list = eme_bbox_list
        self.llines = llines

        # analytics
        self.sentences = self.construct_sentence()

        # post processing on the sentence, create nscs, label the EME

    def set_parent(self, p):
        self.parent = p

    def get_font(self):
        if self.parent is None:
            raise Exception("Should construct the hierarcy")
        return self.parent.get_font()

    def construct_sentence(self):
        """
        based on the llines to create Sentence

        :return:
        """
        sentences = []
        s = Sentence()

        for lline in self.llines:
            ll_str = lline.get_line()
            if ll_str.count('i.e.') > 0:
                tmp = 1

            for ci, char in enumerate(lline.get_lt_chars()):
                # print char.get_text()

                # several conditions
                # 1. end of a sentence
                # 2. hyphen between two line
                # 3. remove the last change line
                # 4. if two digits around the period, not separator
                if char.get_text() == '.':
                    s_last_2 = ''.join(s.text_list[-2:])
                    s_last_3 = ''.join(s.text_list[-3:])

                    # special process for " i.e.", " e.g.", (i.e. , (e.g.
                    is_ie_case = (s_last_2 == " i") or (s_last_2 == "(i") or (s_last_3 == "i.e")
                    is_eg_case = (s_last_2 == " e") or (s_last_2 == "(e") or (s_last_3 == "e.g")

                    # " al."
                    is_etal_case = (s_last_3 == " al")

                    # digits around
                    is_digits_case = False
                    if ci < len(lline.get_lt_chars())-1 and len(s.text_list) > 0:
                        is_digits_case = s.text_list[-1].isdigit() and lline.get_lt_chars()[ci+1].get_text().isdigit()

                    # if the char in ME
                    #eme_bbox_list
                    is_within_me = bbox_half_overlap_list(char.bbox, self.eme_bbox_list)
                    # TODO, but not the last char

                    if (not is_ie_case) and \
                            (not is_eg_case) and \
                            (not is_etal_case) and \
                            (not is_digits_case) and \
                            (not is_within_me):
                        s.label_nscs_eme(self.eme_bbox_list)
                        s.set_parent(self)
                        sentences.append(s)
                        s = Sentence()
                        continue

                if ci == len(lline.get_lt_chars()) - 2 and char.get_text() == '-':
                    # the hypen means breaking of words
                    continue

                if ci == len(lline.get_lt_chars()) - 1:
                    # the last char is the new line char
                    continue

                s.add_char(char)
                if ci == len(lline.get_lt_chars()) - 2 and char.get_text() != '-':
                    # add extra space for a line split without hyphen
                    s.add_text(" ")

        # the last non-empty sentence here
        if len(str(s)) > 0:
            s.label_nscs_eme(self.eme_bbox_list)
            s.set_parent(self)
            sentences.append(s)

        return sentences

    def get_UGPs(self):
        """
        create a list of unorganized group path struct.
        assume that the sentences is constructed,
         then for each sentence, call get UGP

        :return:
        """
        ugp_list = []
        for s in self.sentences:
            ugp_list.extend(s.get_UPGs())
        return ugp_list

    def create_xml_node(self, root_node):
        """

        :param root_node: the higher level node for paragraph block is section
        :return:
        """
        paragraph_node = ET.SubElement(root_node, "Paragraph")
        for sentence in self.sentences:
            sentence_node = ET.SubElement(paragraph_node, "Sentence")
            sentence_str = sentence.export_latex()
            if isinstance(sentence_str, unicode):
                sentence_node.text = sentence_str
            else:
                sentence_node.text = sentence_str.decode('utf-8', 'ignore')

    def export_plain_txt(self):
        """
        for the sentence, export as plain text

        :return:
        """
        block_str = ""
        for sentence in self.sentences:
            block_str += "[Line] {}".format(sentence.export_latex())
        return block_str