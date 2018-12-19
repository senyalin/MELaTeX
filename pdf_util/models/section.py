import xml.etree.ElementTree as ET
from pdfxml.pdf_util.models.block_paragraph import ParagraphBlock
from pdfxml.pdf_util.models.block_ime import IMEBlock

LINE_IME = range(8)


class Section(object):
    """
    In the PDFDoc analysis, based on the title
    regex to split the document into sections,

    And in this class, split the section into
     blocks, for IME, Paragraph
    """
    def __init__(self):
        self._title = None  # assume to be of string type
        self.parent = None

        # raw data as layout lines
        self._llines = []

        # the processed data as blocks
        # the block could be ParagraphBlock, IMEBlock
        self._blocks = []

        self._subsections = []

    def __str__(self):
        if self._title:
            return self._title
        else:
            return "empty title"

    def set_parent(self, p):
        self.parent = p

    def get_font(self):
        if self.parent is None:
            raise Exception("Should construct the hierarcy")
        return self.parent.get_font()

    def set_title(self, title):
        self._title = title

    def set_lline(self, llines, eme_bbox_list):
        """

        :param llines:
        :type llines: list[LayoutLine]
        :param eme_bbox_list:
        :return:
        """
        self._llines = llines

        #self._blocks = create_blocks(self._llines, eme_bbox_list)
        l_idx = 0
        block_llines = []  # store mixed ME-plaintext part
        while l_idx < len(self._llines):
            if self._llines[l_idx].type == LINE_IME:
                if len(block_llines) > 0:
                    b = ParagraphBlock(block_llines, eme_bbox_list)
                    b.set_parent(self)
                    self._blocks.append(b)
                # the IME block here
                ime_b = IMEBlock(self._llines[l_idx].get_lt_chars())
                ime_b.set_parent(self)
                self._blocks.append(ime_b)
                block_llines = []  # re-init
            else:
                block_llines.append(self._llines[l_idx])
            l_idx += 1

        if len(block_llines) > 0:
            b = ParagraphBlock(block_llines, eme_bbox_list)
            b.set_parent(self)
            self._blocks.append(b)

    def add_sub_section(self, sub_section):
        self._subsections.append(sub_section)

    def get_title(self):
        return self._title

    def get_llines(self):
        return self._llines

    def get_blocks(self):
        """

        :return:
        :rtype: list[Block]
        """
        return self._blocks

    def get_UGPs(self):
        """

        :return:
        """
        me_ugp_list = []
        for block in self._blocks:
            if isinstance(block, IMEBlock):
                # TODO, create ugp from IMEBlock
                me_ugp_list.append(block.get_UGP())
            elif isinstance(block, ParagraphBlock):
                me_ugp_list.extend(block.get_UGPs())
            else:
                raise Exception("Unknow block type {}".format(type(block)))
        return me_ugp_list

    def get_IME_UGPs(self):
        """
        only get the UGP of IME
        :return:
        """
        ime_ugp_list = []
        for block in self._blocks:
            if isinstance(block, IMEBlock):
                ime_ugp_list.append(block.get_UGP())
        return ime_ugp_list


    def create_xml_node(self, root_node):
        """

        :param root_node: element tree, XML node
        :return:
        """
        # create the section element
        section_node = ET.SubElement(root_node, "Section")
        section_node.set("title", self._title)

        # enumerate through the blocks
        # enumerate through the sub-sections
        for block in self._blocks:
            if isinstance(block, IMEBlock):
                ime = ET.SubElement(section_node, "IME")
                ime_str = block.get_latex()
                if isinstance(ime_str, unicode):
                    ime.text = ime_str
                else:
                    ime.text = ime_str.decode("utf-8")
            elif isinstance(block, ParagraphBlock):
                block.create_xml_node(section_node)
            else:
                raise Exception("Unknow block type {}".format(type(block)))

    def export_plain_text(self):
        """
        based on different type of section to export differently
        :return:
        """
        section_str = "[Section] {}\n".format(self.get_title())
        if self.get_title().count("Reference") == 0:
            # normal section
            for block in self._blocks:
                section_str += block.export_plain_txt()+"\n"
        else:
            for line in self._llines:
                section_str += "[Line] {}\n".format(line.get_line().strip())
