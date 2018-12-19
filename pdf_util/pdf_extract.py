# -*- coding: utf-8 -*-
import os
import copy, pickle
from pdfxml.path_util import get_tmp_path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal, LTChar, LTAnno
from pdfminer.layout import LTRect, LTLine, LTCurve, LTFigure

from pdfxml.file_util import load_general, dump_general, load_serialization, dump_serialization
debug = False


def get_page_num(fpath):
    """ Get the page number for the current pdf file
    https://stackoverflow.com/questions/45841012/how-can-i-get-the-total-count-of-total-pages-of-a-pdf-using-pdfminer-in-python
    """
    tmp_path = get_tmp_path(fpath)
    cache_path = "{}.page_num.json".format(tmp_path)
    if os.path.isfile(cache_path):
        tmp_dict = load_general(cache_path)
        return tmp_dict['page_num']

    # Open a PDF file.
    fp = open(fpath, 'rb')
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser)

    c = resolve1(document.catalog['Pages'])['Count']

    tmp_dict = {'page_num': c}
    dump_general(tmp_dict, cache_path)

    return c


def print_layout(l, char_list):
    """ get all the chars
    """
    for e in l:
        if isinstance(e, LTTextLineHorizontal):
            #Try recursively text line"
            print_layout(e, char_list)
        elif isinstance(e, LTTextBoxHorizontal):
            #Try recursively text box"
            print_layout(e, char_list)
        elif isinstance(e, LTChar) or isinstance(e, LTAnno):
            char_list.append(e)
        elif isinstance(e, LTRect):
            # TODO, store as the candidates for the fraction
            pass
        elif isinstance(e, LTLine):
            # highly related with table
            pass
        elif isinstance(e, LTCurve):
            #print type(e), e.get_pts(), e.linewidth
            pass
        elif isinstance(e, LTFigure):
            # TODO, process figure
            pass
        else:
            if debug:
                print e, type(e)


def get_pdf_page_bbox_abandon(fname, pid=0):
    """
    Get the page number for the current pdf file
    NOTE that different page might have different number of pages
    could possible be the fraction lines, or the lines for the radical elements

    :param fname:
    :param pid:
    :return: tuple(left, xx, right, xx), only the last two value are valid for
    """
    # Open a PDF file.
    fp = open(fname, 'rb')
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for i, page in enumerate(PDFPage.create_pages(document)):
        if i == pid:
            interpreter.process_page(page)
            return page.cropbox
    return None


def adjust_element_bbox(elem, crop_bbox):
    """

    :param elem:
    :param crop_bbox:
    :return:
    """
    bbox = elem.bbox
    new_bbox = [
        bbox[0] - crop_bbox[0],
        bbox[1] - crop_bbox[1],
        bbox[2] - crop_bbox[0],
        bbox[3] - crop_bbox[1]
    ]
    elem.set_bbox(new_bbox)


def process_pdf_internal(fname, page_num='all'):
    """
    Change from orignal name of process_pdf to process_pdf_internal
    get the raw character

    :param fname:
    :param page_num:
    :return:
    """
    tmp_path = get_tmp_path(fname)
    cache_path = "%s.chars.%s.pkl"%(tmp_path, str(page_num))

    if os.path.isfile(cache_path):
        try:
            return pickle.load(open(cache_path))
        except Exception as e:
            print "load failed, get again"

    # global char_list
    char_list = []
    if debug:
        print fname
    # Open a PDF file.
    fp = open(fname, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for i, page in enumerate(PDFPage.create_pages(document)):
        process_mark = (page_num == 'all' or page_num == i)
        if process_mark:
            interpreter.process_page(page)
            layout = device.get_result()
            print_layout(layout, char_list)

        if page_num == i:
            break

    crop_bbox = get_pdf_page_bbox_abandon(fname, page_num)
    for char in char_list:
        if isinstance(char, LTChar):
            adjust_element_bbox(char, crop_bbox)

    with open(cache_path, 'w') as f:
        pickle.dump(char_list, f)
    return char_list


def adjust_basedon_glyph_ratio(char_list, pdf_path, pid):
    """

    :param char_list:
    :param pdf_path:
    :return: No return value
    """
    # create glyph ratio
    from pdfxml.pdf_util.font_process import get_glyph_ratio
    from pdfxml.pdf_util.font_process import get_font_from_pdf
    from pdfxml.pdf_util.char_process import get_char_glyph

    fontname2glyphname2adjust = get_glyph_ratio(pdf_path, pid)
    font = get_font_from_pdf(pdf_path, pid)
    for cid, char in enumerate(char_list):
        if not isinstance(char, LTChar):
            continue
        fontname = char.fontname
        glyphname = get_char_glyph(char, font)
        if fontname in fontname2glyphname2adjust and \
                glyphname in fontname2glyphname2adjust[fontname]:
            up_ratio, lower_ratio = fontname2glyphname2adjust[fontname][glyphname]
            org_top = char.bbox[3]
            org_bottom = char.bbox[1]
            height = org_top - org_bottom
            new_top = org_top - height*up_ratio
            new_bottom = org_top - height*lower_ratio
            char.set_bbox([char.bbox[0], new_bottom, char.bbox[2], new_top])


def process_pdf_path(fname, page_num='all'):
    """
    Extract the path, which might be part of the ME, such as fraction line

    :param fname:
    :param page_num:
    :return:
    """
    if page_num == 'all':
        raise Exception("Not support get all at once")

    def print_layout(l):
        """get all the path such as fraction line and line for radical
        """
        for e in l:
            if isinstance(e, LTTextLineHorizontal) or isinstance(e, LTTextBoxHorizontal):  # recursively get the path
                print_layout(e)
            elif isinstance(e, LTRect) or isinstance(e, LTLine):
                # LTLine related with table
                # TODO, store as the candidates for the fraction
                path_list.append(e)
            else:
                # LTCurve might be related to the figure and drawings
                if debug:
                    print e, type(e)

    path_list = []
    fp = open(fname, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)

    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for i, page in enumerate(PDFPage.create_pages(document)):
        process_mark = (page_num == 'all' or page_num == i)
        if process_mark:
            interpreter.process_page(page)
            layout = device.get_result()
            print_layout(layout)
        if page_num == i:
            break

    crop_bbox = get_pdf_page_bbox_abandon(fname, page_num)

    # adjust the element bbox based on the crop bbox
    for path in path_list:
        adjust_element_bbox(path, crop_bbox)

    return path_list


def process_pdf_lines(fname, page_num='all', do_adjust=False):
    """

    :param fname: file path to the PDF file
    :param page_num: default to extract all
    :return:
    :rtype: list(list(LTChar))
    """
    # TODO, cache the informatin here?
    from pdfxml.path_util import get_tmp_path
    tmp_pdf_path = get_tmp_path(fname)

    pdf_lines_cache = "{}.pdf_line.{}.pkl".format(tmp_pdf_path, page_num)
    if os.path.isfile(pdf_lines_cache):
        return load_serialization(pdf_lines_cache)

    line_list = []
    char_list = []
    def print_layout(l):
        """ get all the chars
        """
        for e in l:
            if isinstance(e, LTTextLineHorizontal):
                #print "try recursively text line"
                print_layout(e)
                line_list.append(copy.copy(char_list))
                while len(char_list) > 0:
                    char_list.pop()

            if isinstance(e, LTTextBoxHorizontal):
                #print "try recursively text box"
                print_layout(e)

            if isinstance(e, LTChar) or isinstance(e, LTAnno):
                char_list.append(e)


    fp = open(fname, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for i, page in enumerate(PDFPage.create_pages(document)):
        process_mark = (page_num == 'all' or page_num == i)
        if process_mark:
            interpreter.process_page(page)
            layout = device.get_result()
            print_layout(layout)

        if page_num == i:
            break

    if do_adjust:
        for line in line_list:
            adjust_basedon_glyph_ratio(line, fname, page_num)

    # adjust based on crop bbox
    crop_bbox = get_pdf_page_bbox_abandon(fname, page_num)
    for line in line_list:
        for char in line:
            if isinstance(char, LTChar):
                adjust_element_bbox(char, crop_bbox)

    dump_serialization(line_list, pdf_lines_cache)
    return line_list