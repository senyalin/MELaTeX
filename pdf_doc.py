import re
import xml.etree.ElementTree as ET
from pdfxml.pdf_util.pdf_extract import get_page_num
from pdfxml.debug_util import debug_info
from pdfxml.me_extraction.me_font_stat_stage4 import stage4_font_stat
from pdfxml.me_extraction.ME_separation import extract_me
from pdfxml.pdf_util.models.layout_page import LayoutPage
from pdfxml.me_util import load_eme_bbox_list
from pdfxml.xml_util import clean_xml
from pdfxml.pdf_util.models.section import Section


def section_level(sec_title):
    """
    This is only specialized for the NIPS papers

    abstraction, ack, ref are special ones
    the begin part should be ignored

    count how many \d\. pattern
    """
    l = len(re.findall(r'\d\.', sec_title))
    if l == 0:
        # the NIPS level1 heading don't have dot after the number
        return 1
    else:
        return l


class PDFDoc:
    """
    TODO, one thing need clarify is how is page information for section being organized,
    As one section might span multiple pages
    """
    def __init__(self, pdf_path):
        """
        :param pdf_path: file path for the PDF file
        """
        # raw data
        self.pdf_path = pdf_path

        pn = get_page_num(pdf_path)
        print "# of Pages: ", pn
        # batch processing here
        # * font
        self.font = None  # the font is not that useful for now.

        # * stage4_font_stat
        stage4_font_stat(pdf_path)
        debug_info("DONE font stat for ME extraction")

        # * batch ime & eme
        # Not using the parallel processing as
        # there might be a bug here causing the failure of cache checking
        extract_me(pdf_path)
        debug_info("DONE ime & eme extraction")

        # raw layout pages
        self.pages = [LayoutPage(pdf_path, pid) for pid in range(pn)]

        # processed data
        self.sections = []       # plain sections
        self.root_sections = []  # the root of sections after the hierarchy is built
        self.create_plain_section()
        self._create_section_hierarchy()

    ###############################
    #  Normalized data structure  #
    ###############################
    def create_plain_section(self):
        cur_title = "Begin"
        cur_lines = []
        eme_bbox_list = []
        for pi, page in enumerate(self.pages):
            eme_bbox_list = load_eme_bbox_list(self.pdf_path, pi)

            for line in page.get_layout_lines():  # enumeration of layout line here
                # TODO, only do the regex matching,
                # not using the font based title checking
                # major_font = line.get_major_font()
                if line.check_line_section_title():
                    s = Section()
                    s.set_title(cur_title)
                    s.set_lline(cur_lines, eme_bbox_list)
                    if len(cur_lines) > 0:
                        s.set_parent(self)
                        self.sections.append(s)

                    cur_title = line.get_line().strip()
                    cur_lines = []
                else:
                    cur_lines.append(line)
            tmp = 1
            # could not processing skip page cases for now
            if len(cur_lines) > 0:
                # the last section
                s = Section()
                s.set_title(cur_title)
                s.set_lline(cur_lines, eme_bbox_list)
                s.set_parent(self)
                self.sections.append(s)

            cur_title = "NewPage"
            cur_lines = []

    def _create_section_hierarchy(self):
        level_id_s = []
        sid2psid = {}
        for i, sec in enumerate(self.sections):
            ":type sec: Section"
            l = section_level(sec.get_title())

            while len(level_id_s) >= l:
                del level_id_s[-1]

            # build the parent relationship here
            if len(level_id_s) == 0:
                sid2psid[i] = -1
            else:
                sid2psid[i] = level_id_s[-1][1]
            level_id_s.append((l, i))

        root_sections_idx = []
        for sid, pid in sid2psid.items():
            if pid == -1:
                root_sections_idx.append(sid)
        root_sections_idx.sort()

        # add the children section as a block of the parent section
        for sid, pid in sid2psid.items():
            if pid == -1:
                continue
            # print "add", sections[sid]['title'], 'as subsection of', sections[pid]['title']
            self.sections[pid].add_sub_section(self.sections[sid])

        self.root_sections = [self.sections[si] for si in root_sections_idx]


    #########
    # raw data processing
    #########
    def get_f2c(self):
        # get font 2 count
        return self.f2c

    def get_font(self):
        return self.font


    ############
    #  export  #
    ############
    def export_plain_txt(self, out_path):
        if len(self.sections) == 0:
            raise Exception("No section and sentence extracted")

        with open(out_path, 'w') as f:
            for section in self.sections:
                ":type section: Section"
                print>> f, section.export_plain_text().encode("utf-8")

    def create_xml_node(self):
        rn = ET.Element("PDFDoc")
        # for section in self.root_sections:
        # TODO, not building hierarchy now
        for section in self.sections:
            section.create_xml_node(rn)
        return rn

    def get_UGPs(self):
        """
        export all the information required to analyze the ME, as UnorganizedGroupPath

        :return:
        """
        me_ugp_list = []
        for section in self.sections:
            me_ugp_list.extend(section.get_UGPs())
        return me_ugp_list

    def get_IME_UGPs(self):
        """
        only get the IMEs
        :return:
        """
        me_ugp_list = []
        for section in self.sections:
            me_ugp_list.extend(section.get_IME_UGPs())
        return me_ugp_list

    def export_xml(self, out_path):
        """
        export the document as XML

        In sections, there is a list of paragraphs,
        Could also be followed by sections of next level
        """
        root_node = self.create_xml_node()
        #res = ET.tostring(root_node, encoding='utf-8')
        res = ET.tostring(root_node)
        clean_txt = res
        with open(out_path, 'w') as f:
            # print>>f, res.encode('utf-8')
            print>> f, clean_txt
        clean_xml(out_path)