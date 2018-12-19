# -*- coding:utf-8 -*-

"""
7098, the symbols are in the file, but could not read them out
FNQGDO+CMSY7:0,?,minus;3,?,asteriskmath;62,null,latticetop;106,|,bar;121,†,dagger;122,‡,daggerdbl;

font based seperation of text with Math
"""

import locale
import os
import pickle

from pdfxml.pdf_util.exceptions import UnknownUnicodeException
from pdfxml.pdf_util.pdf_extract import process_pdf_internal
from pdfminer.layout import LTChar
from pdfxml.loggers import pdf_util_error_log, general_logger

from pdfxml.me_taxonomy.math_resources import special_unicode_chars, unicode2latex
from pdfxml.path_util import get_tmp_path


def get_font_name_suffix(font_name):
    if '+' in font_name:
        return font_name[font_name.index('+')+1:]
    return font_name


#############
# using PDFBox to read all char information
#############
def get_font_from_pdf(pdf_path, pid):
    """
    This is the most commonly used file

    NOTE, using the pdfbox to export the glyph

    :param pdf_path:
    :return:
    """
    return None
    tmp_path = get_tmp_path(pdf_path)
    font_path = "{}.font".format(tmp_path)

    if not os.path.isfile(font_path):
        export_font(pdf_path, font_path)

    page2name2detail = read_pdfbox_font(font_path)
    return page2name2detail[pid]	
	
	
#############
# using PDFBox to read all char information
#############
#def export_font(pdf_path, export_path):
    """
    extract the CMAP font information using pdfbox
    :param pdf_path:
    :param export_path: path to the export txt file
    :return:
    """
#    if os.path.isfile(export_path):
#        return
#    cmd = "java -jar %s/pdfbox_font/target/readfont.jar-jar-with-dependencies.jar %s > %s" % (
#        PDF_UTIL_PATH, pdf_path, export_path)
#    os.system(cmd)


def read_pdfbox_font(export_path):
    """
    TODO, use new seperator to avoid bug
    :param export_path: the exported font information from PDFBox
    :return:
    """
    # find all page, and only keep one copy of the mapping
    if not os.path.isfile(export_path):
        raise Exception("Font file {} not found".format(export_path))

    content = open(export_path).read()
    encoding_name = locale.getdefaultlocale()[1]
    content = content.decode(encoding_name)

    pages = content.split("page")
    name2detail = {}
    page2name2detail = {}
    for page in pages:
        if page.strip() == "":
            continue
        lines = page.split("\n")
        pid = int(lines[0])
        lines = lines[1:]
        tmp_name2detail = {}
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            cidx = line.index(":")
            name = line[:cidx]
            detail = line[cidx+1:]
            #name, detail = line.strip().split(":")
            if name in name2detail:
                continue
            chars = detail.split(";")
            char_tuple_list = []
            for char in chars:
                if char == "":
                    continue
                try:
                    i1 = char.index(",")
                    i2 = char.rindex(",")
                    aval = int(char[:i1])
                    unival = char[i1+1:i2]
                    glyval = char[i2+1:]
                    char_tuple_list.append( [aval, unival, glyval] )
                except:
                    # TODO, the ; or the , are in the font
                    pass

            name2detail[name] = char_tuple_list
            tmp_name2detail[name] = char_tuple_list
        page2name2detail[pid] = tmp_name2detail

    #return name2detail
    return page2name2detail


##############
# Adjustment of the glyph ratio
##############
def export_glyph_ratio(pdf_path):
    """
    TODO
    :param pdf_path:
    :return:
    """
    raise Exception("should not call it")
    tmp_pdf_path = get_tmp_path(pdf_path)
    print "TODO, move the glyph JAR into common place"
    export_glyph_jar_path = "E:/pdfbox-2.0.8-src/pdfbox-2.0.8/debugger/target/pdfGlyphAdjust-jar-with-dependencies.jar"
    cmd = "java -jar {} {}".format(export_glyph_jar_path, tmp_pdf_path)
    os.system(cmd)


def get_glyph_ratio(pdf_path, pid):
    """
    TODO, what the return should be like?

    :param pdf_path:
    :param pid:
    :return: page to fontname 2 glyphname 2 pair/tuple
    """
    raise Exception("Should not call it")

    import shutil
    from pdfxml.path_util import get_tmp_path
    from pdfxml.pdf_util.pdf_extract import get_page_num
    tmp_pdf_path = get_tmp_path(pdf_path)
    if tmp_pdf_path == pdf_path or os.path.isfile(tmp_pdf_path):
        pass
    else:
        shutil.copy(pdf_path, tmp_pdf_path)
    pn = get_page_num(pdf_path)
    all_create = True  # check whether all created
    for i in range(pn):
        gr_path = "{}.glyphratio.{}.txt".format(tmp_pdf_path, i)
        if not os.path.isfile(gr_path):
            all_create = False
            break
    if not all_create:
        export_glyph_ratio(pdf_path)

    # read from the files and return here
    #page2fontname2glyphname2adjust = {}
    #for pid in range(pn):
    fontname2glyphname2adjust = {}
    gr_path = "{}.glyphratio.{}.txt".format(tmp_pdf_path, pid)
    lines = open(gr_path).readlines()
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        ws = line.strip().split("\t")
        fontname, glyphname, up_ratio, lower_ratio = \
            ws[0], ws[1], float(ws[2]), float(ws[3])
        if fontname not in fontname2glyphname2adjust:
            fontname2glyphname2adjust[fontname] = {}
        fontname2glyphname2adjust[fontname][glyphname] = (up_ratio, lower_ratio)

        #page2fontname2glyphname2adjust[pid] = fontname2glyphname2adjust
    #return page2fontname2glyphname2adjust

    return fontname2glyphname2adjust


##############
# statistic of font usage
##############
def get_major_font_name_by_pdf_path(pdf_path):
    """

    :param pdf_path:
    :return:
    """
    pass


def get_major_font_name_of_char_list(char_list):
    """
    get the major font by char

    :param char_list:
    :return:
    """
    fn2c = {}
    for c in char_list:
        if not isinstance(c, LTChar):
            continue
        fn = c.fontname
        if fn2c.has_key(fn):
            fn2c[fn] += 1
        else:
            fn2c[fn] = 1

    fn_list = fn2c.keys()
    fn_list.sort(key=lambda fn:-fn2c[fn])
    if len(fn_list) == 0:
        raise Exception("no char in the file?")
    else:
        return fn_list[0]

def font2count(fpath):
    """
    statistic of the count of each font setting

    :param fpath: path of pdf file
    :return: font name 2 the count
    :rtype: dict(str, int)
    """
    cache_path = "%s.f2c.pkl"%(fpath)

    if os.path.isfile(cache_path):
        return pickle.load(open(cache_path))

    chars = process_pdf_internal(fpath)
    font2count = {}
    for char in chars:
        if isinstance(char, LTChar):
            if not font2count.has_key(char.fontname):
                font2count[char.fontname] = 0
            font2count[char.fontname] += 1

    with open(cache_path, 'w') as f:
        pickle.dump(font2count, f)

    return font2count


def get_char_glyph(char, font, debug=False):
    """
    FNQGDO+CMSY7:0,?,minus;3,?,asteriskmath;62,null,latticetop;106,|,bar;121,†,dagger;122,‡,daggerdbl;

    :param char:
    :type char: LTChar
    :param font: fontname-> [(ascii, unicode, glyphname)]
    :type font: dict(str, list[tuple])
    :return: return None if there is no glyph name
    """
    if font is None:
        return char.get_text()

    uval = char.get_text()
    char_av = None
    if len(uval) > 1:
        if uval.count('cid') > 0:
            char_av = int(uval[uval.index(':') + 1:uval.index(')')])
    else:
        if ord(uval) < 128:
            char_av = ord(uval)

    fn = char.fontname
    if fn in font:
        for av, uv, gn in font[fn]:
            if (char_av is not None) and av == char_av:
                return gn
        for av, uv, gn in font[fn]:
            if uv == uval:
                return gn

    unicode2gn = {
        u'\u210e': 'h',
    }

    if not isinstance(char, LTChar):
        return None

    if debug:
        if len(uval) == 1:
            general_logger.debug("{} {} {}".format(
                    uval.encode("utf-8"), len(uval), ord(uval)))
        else:
            general_logger.debug("{} {}".format(
                uval.encode("utf-8"), len(uval)))

    # unicode in ascii range?
    char_av = None
    #http://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
    if len(uval) > 1:
        if uval.count('cid') > 0:
            #  the following part is about the cid mapping
            char_av = int(uval[uval.index(':')+1:uval.index(')')])
            if debug:
                general_logger.debug("cid map {}".format(char_av))

        elif uval in ['ff', 'fi']:
            return uval
        elif uval >= u'\U0001d44e' and uval <= u'\U0001d467':
            # MS equation using the following fonts ABCDEE+Cambria
            #print uval, type(uval)
            tmp = u'\U0001d44e'
            # Check out the history to a series of trial to make this work
            return chr(ord(uval[1])-ord(tmp[1])+ord('a'))
        else:
            print "meet uval as", uval, len(uval)
            raise Exception("TODO, enhance the logic here")
            # 1. if not a simple code,
            # case 1.1 start with \x , transform into the char av
            # case 1.2 start with \u, get the unicode value, and try to match
    else:
        if ord(uval) < 128:
            char_av = ord(uval)
            return uval

        elif uval in unicode2gn:
            return unicode2gn[uval]
        elif uval in special_unicode_chars:
            return uval
        elif uval in unicode2latex:
            latex_val = unicode2latex[uval]
            return latex_val[1:] if latex_val.startswith("\\") else latex_val
        else:
            # https://stackoverflow.com/questions/27435855/how-does-one-print-a-unicode-character-code-in-python

            pdf_util_error_log.error("single length uval {}".format(uval.encode('utf-8')))
            pdf_util_error_log.error("single uval unicode {}".format(uval.encode('raw_unicode_escape')))

            #print uval.encode('hex')
            raise UnknownUnicodeException(uval)

    # TODO, it seems that it means the index in the font_dict?
    # NIPS_2016_6589.pdf
    if uval == u'\x01':
        return font[char.fontname][1][2]

    if debug:
        # TODO,     print font[fn]
        # KeyError: 'SOKHPF+NimbusRomNo9L-Regu'
        # Not sure why this error occur
        #print font[fn]
        pass

    if fn == 'unknown' and "cid" in uval:
        general_logger.warning("Meet unknown font name for {}".format(uval))
        val = uval[uval.index(':')+1:-1]
        return chr(int(val))

    return None
