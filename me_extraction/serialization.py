import re
import struct
import sys
import xml.etree.ElementTree as ET
from pdfminer.layout import LTChar
from pdfxml.pdf_util.char_process import get_latex_val_of_lt_char
from pdfxml.pdf_util.font_process import get_font_from_pdf
from pdfxml.pdf_util.layout_util import get_char_list_bbox
from pdfxml.pdf_util.bbox import BBox


illegal_xml_re = re.compile(u'[\x00-\x08\x0b-\x1f\x7f-\x84\x86-\x9f\ud800-\udfff\ufdd0-\ufddf\ufffe-\uffff]')


def invalid_xml_remove(c):
    #http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
    illegal_unichrs = [ (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
                    (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
                    (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
                    (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                    (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
                    (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                    (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
                    (0x10FFFE, 0x10FFFF) ]

    illegal_ranges = ["%s-%s" % (unichr(low), unichr(high))
                  for (low, high) in illegal_unichrs
                  if low < sys.maxunicode]

    illegal_xml_re = re.compile(u'[%s]' % u''.join(illegal_ranges))
    bad_char_list = ['\xb0', '\xb6', '\xb2', '\xab', '\xac', '\xaa', '\xba']

    # remove larger than >= 128
    # not quite sure here, assume all ascii not UTF-8
    clean_larger_than_128 = ""
    for one_c in c:
        one_c_val = ord(one_c)
        if one_c_val >= 128:
            continue
        clean_larger_than_128 += one_c
    c = clean_larger_than_128

    for bad_char in bad_char_list:
        try:
            c = c.replace(bad_char, '')  # lead to encoding error
        except Exception as e:

            print 'ignore back value', c
            print e

    try:
        c.decode('utf-8')
    except Exception as e:
        print "TODO log the error", e
        return ' '

    if illegal_xml_re.search(c) is not None:
        #Replace with space
        return ' '
    else:
        return c


def double2hexlongbits(double):
    i = struct.unpack('Q', struct.pack('d', double))
    # print i, format(i, 'x')
    res = format(int(i[0]), 'x')
    return res


def icst_bbox2str(bbox):
    if isinstance(bbox, BBox):
        res = "%s %s %s %s" % (
            double2hexlongbits(bbox.left()),
            double2hexlongbits(bbox.top()),
            double2hexlongbits(bbox.right()),
            double2hexlongbits(bbox.bottom())
        )
    else:
        # the str is in the order of left, top, right, bottom
        res = "%s %s %s %s"%(
            double2hexlongbits(bbox[0]),
            double2hexlongbits(bbox[3]),
            double2hexlongbits(bbox[2]),
            double2hexlongbits(bbox[1])
            )
    return res


def readable_bbox2str(bbox):
    """
    bbox as left, bottom, right, top

    :param bbox:
    :return:
    """
    if isinstance(bbox, BBox):
        res = " ".join([str(v) for v in bbox.to_list()])
    else:
        res = " ".join([str(v) for v in bbox])
    return res


def export_xml(page_info, out_path, pdf_path=None, pid=None):
    """
    TODO, also export the value human could understand, rather than the hex value
    hex value is only for consistency with the other system
    """
    page_n = ET.Element('Page', {'PageNum': str(page_info['pid'])})
    font = get_font_from_pdf(pdf_path, pid)

    for ime_line in page_info['ilist']:
        bbox = get_char_list_bbox(ime_line)

        i_n = ET.SubElement(
            page_n,
            'IsolatedFormula',
            {
                'BBox': icst_bbox2str(bbox),
                'readable_bbox': readable_bbox2str(bbox)
            })

        for char in ime_line:
            if isinstance(char, LTChar):
                clean_text = get_latex_val_of_lt_char(char, font)
                clean_text = invalid_xml_remove(clean_text)
                #print clean_text

                #clean_text = illegal_xml_re.sub('', char.get_text())
                c_n = ET.SubElement(
                    i_n,
                    'Char',
                    {
                        'BBox': icst_bbox2str(char.bbox),
                        'readable_bbox': readable_bbox2str(char.bbox),
                        'FSize': str(char.size),
                        'Text': clean_text
                    })

    # the eme part
    for eme in page_info['elist']:
        bbox = get_char_list_bbox(eme)

        i_n = ET.SubElement(
            page_n,
            'EmbeddedFormula',
            {
                'BBox':icst_bbox2str(bbox),
                'readable_bbox':readable_bbox2str(bbox)
            })
        for char in eme:
            if isinstance(char, LTChar):
                #clean_text = illegal_xml_re.sub('', char.get_text())
                clean_text = get_latex_val_of_lt_char(char, font)
                clean_text = invalid_xml_remove(clean_text)
                #print clean_text
                c_n = ET.SubElement(
                    i_n,
                    'Char',
                    {
                        'BBox': icst_bbox2str(char.bbox),
                        'readable_bbox': readable_bbox2str(char.bbox),
                        'FSize': str(char.size),
                        'Text': clean_text
                    })

    try:

        res = ET.tostring(page_n, encoding='utf-8')
        if out_path:
            with open(out_path, 'w') as f:
                print>>f, res
        else:
            print res

    except Exception as e:
        print e