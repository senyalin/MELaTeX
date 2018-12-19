"""
Wrapper to get the analytics from pdfbox
"""

import os
import re

import numpy as np
import string
import traceback
from pdfxml.path_util import change2website_root
from pdfxml.me_taxonomy.math_resources import unicode2latex, unicode2gn, str2gn
from pdfxml.pdf_util.bbox import BBox
from pdfxml.InftyCDB.name2latex import normal_fence_mapped, name2latex
from pdfxml.path_util import get_tmp_path
from pdfxml.pdf_util.word_seg_process import create_char
from pdfxml.pdf_util.char_process import get_one_ltchar, simplify_glyph
from pdfxml.pdf_util.pdf_extract import get_page_num
from pdfxml.loggers import pdf_util_error_log


def pdf_extract_chars(pdf_path, pid=0):
    """
    return list of chars as well as their glyph

    :param pdf_path:
    :param pid:
    :return:
        list of LTChars based on the layout analysis of the
        each LTChar is also associated with the glyph names,

        The priority for the name: glyph -> unicode value -> code
    """
    page_size = get_pdf_page_size(pdf_path, pid)

    lt_char = get_one_ltchar()

    char_list = []
    lines = get_exported_char_lines(pdf_path, pid)

    for line in lines:
        if line.startswith("CHARINFO"):
            ws = line.strip().split('\t')
            # if there is a non digit one, keep the one
            # otherwise could only inference based on the digit

            if len(ws) < 5:
                ttt = 1
                #pass
                continue

            val = get_char_val(ws, line)
            #print "YaY"

            # might be the value is \t
            bbox = None
            for tmpi in range(5, len(ws)):
                if ws[tmpi].count(',') == 3:
                    bbox = [float(v) for v in ws[tmpi].split(',')]
                    break

            for v in bbox:
                pass

            if len(bbox) != 4:
                raise Exception('bbox error')

            new_top = page_size['height'] - bbox[1]
            new_bottom = page_size['height'] - bbox[3]
            bbox[1], bbox[3] = new_bottom, new_top

            # use the original parenthesis, for mathcing of citation
            if val in normal_fence_mapped.keys():
                # ws[3]  # the unicode value part
                val = normal_fence_mapped[val]


            if val == 'null':
                tttt = 1
            if simplify_glyph(val) == 'null':
                ttt = 1
            c = create_char(
                lt_char,
                simplify_glyph(val),
                ws[1],
                bbox)
            #c.width = float(ws[6])  # the space for the following char
            # need some transformation to make it right
            char_list.append(c)
    #for char in char_list:
    #    print char
    return char_list


def get_page_char_path(pdf_path, pid):
    """
    the exported information from pdfbox

    :param pdf_path:
    :param pid:
    :return:
    """
    tmp_pdf_path = get_tmp_path(pdf_path)
    page_char_path = "{}.{}.txt".format(tmp_pdf_path, pid)
    return page_char_path


def export_exact_position_by_page(pdf_path, pid):
    EXPORT_CHAR_JAR_NAME = "pdfbox-examples-2.0.8-jar-with-dependencies.jar"
    #print "Current Directory: ", os.getcwd()
    cmd = "java -jar {} {} {}".format(EXPORT_CHAR_JAR_NAME, pdf_path, pid)
    os.system(cmd)


def export_exact_position_by_page_wrapper(args):
    export_exact_position_by_page(*args)


def export_exact_position(pdf_path, the_pid=None):
    """
    export the tight bounding box of each char
    :param pdf_path:
    :return:
    """
    from pdfxml.path_util import JAR_FOLDER
    # checking here
    pn = get_page_num(pdf_path)

    tmp_pdf_path = get_tmp_path(pdf_path)

    if the_pid is not None:
        out_path = "{}.{}.txt".format(tmp_pdf_path, the_pid)
        if os.path.isfile(out_path):
            return
    else:
        all_done = True
        for i in range(pn):
            out_path = "{}.{}.txt".format(tmp_pdf_path, i)
            if not os.path.isfile(out_path):
                all_done = False
        if all_done:
            print("All Extracted for the exact postion and glyph")
            return

    EXPORT_CHAR_JAR_NAME = "pdfbox-examples-2.0.8-jar-with-dependencies.jar"
    os.chdir(JAR_FOLDER)

    if the_pid is None:
        print "JAR_FOLDER: ", JAR_FOLDER
        cmd = "java -jar {} {}".format(EXPORT_CHAR_JAR_NAME, tmp_pdf_path)
        os.system(cmd)
    else:
        export_exact_position_by_page(tmp_pdf_path, the_pid)

    # because of the paralleization
    change2website_root()

    print("After export exact position {}".format(os.getcwd()))


def check_export(pdf_path, the_pid=None):
    """
    chech whether the exact position is exported.

    :param pdf_path:
    :return:
    """
    if the_pid is None:
        pn = get_page_num(pdf_path)
        run_again = False
        for pid in range(pn):
            # first check the file system
            page_char_path = get_page_char_path(pdf_path, pid)
            if not os.path.isfile(page_char_path):
                run_again = True
        if run_again:
            export_exact_position(pdf_path)
    else:
        export_exact_position(pdf_path, the_pid)


def get_exported_char_lines(pdf_path, pid):
    page_char_path = get_page_char_path(pdf_path, pid)
    lines = []
    with open(page_char_path) as f:
        for line in f:
            lines.append(line)

    return lines


def get_char_val(ws, line):
    """

    :param ws2: is the code
    :param ws3: is the possible ASCII
    :param ws4: is the glyph name
    :return:
    """
    val = None
    """
    for tmp_val in [ws[2], ws[3], ws[4]]:
        if len(tmp_val) == 1 and not tmp_val.isdigit():
            val = tmp_val
    """

    if val is None and ws[4] not in ["", 'null']:
        val = ws[4]
    elif (val is None) and (ws[3] not in ["", 'null']):
        val = ws[3]
    elif val is None and ws[2] not in ["", 'null']:
        val = chr(int(ws[2]))

        # only after the glyph name and unicode not valid
        # try to do such mapping.
        if "TimesNewRoman" in ws[1] or "Arial" in ws[1]:
            # https: // en.wikipedia.org / wiki / Windows - 1252
            i2u = {
                146: 'quoteright',
                150: 'dash',
            }
            int_val = int(ws[2])
            if int_val in i2u:
                val = i2u[int_val]
            else:
                assert int_val < 128
                val = chr(int_val)
    if val in ['null', '']:
        ttt = 1

    try:
        # tmp_uni_val = val
        if isinstance(val, unicode) and val in unicode2latex:
            # tmp_str_val = val.encode('utf-8')
            val = unicode2latex[val]
        elif isinstance(val, str) or isinstance(val, unicode):
            if isinstance(val, unicode):
                val = val.encode('utf-8', 'ignore')
            valid_char_list = string.letters
            valid_char_list += string.whitespace
            valid_char_list += string.digits
            valid_char_list += string.printable
            if val not in valid_char_list:
                if val in str2gn:
                    val = str2gn[val]
                else:
                    tmp_uni_val = val.decode('utf-8')
                    if tmp_uni_val in unicode2latex:
                        val = unicode2latex[tmp_uni_val]
                    elif tmp_uni_val in unicode2gn:
                        val = unicode2gn[tmp_uni_val]
                    elif tmp_uni_val in name2latex:
                        val = tmp_uni_val
                    elif tmp_uni_val in ['ffi', 'fi', 'ff', 'fl']:
                        val = tmp_uni_val
                    elif re.match(r'[a-z]\d+', tmp_uni_val):
                        val = "graphics"
                    else:
                        print "single uval unicode {}".format(tmp_uni_val.encode('raw_unicode_escape'))
                        print tmp_uni_val
                        # raise Exception("TODO")

                        pdf_util_error_log.error(line)
                        val = "badwindows"
    except:
        print traceback.format_exc()
        pdf_util_error_log.error(line)
        val = "badwindows"  # just set as empty

    if val == 'null':
        ttt = 1
    return val


def pdf_extract_words(pdf_path, pid=0):
    """
    return list of words and their bounding box from PDFBox

    NOTE: the word information is not accurate, when there is explict space

    :param pdf_path:
    :param pid:
    :return:
        list of {
            'word': str
            'bbox': BBox
        }
    """
    check_export(pdf_path)

    page_size = get_pdf_page_size(pdf_path, pid)
    page_char_path = get_page_char_path(pdf_path, pid)

    word_list = []
    with open(page_char_path) as f:
        for line in f:
            if line.startswith("WORD:"):
                ws = line.strip().split('\t')

                if len(ws) < 3:
                    # simply ignore the word fornow
                    continue

                pos_list = None
                for tmpi in range(2, len(ws)):
                    if ws[tmpi].count(',') == 3:
                        pos_list = ws[tmpi].split(',')
                        break

                if (pos_list is None) or (len(pos_list) != 4):
                    # just ignore, them for now
                    # even new line char.
                    continue

                # for debug purpose
                #print pdf_path, pid
                #print line
                #print pos_list, pos_list is None

                word_info = {
                    'str': ws[1],
                    'bbox': BBox([
                        float(pos_list[0]),
                        page_size['height'] - float(pos_list[3]),
                        float(pos_list[2]),
                        page_size['height'] - float(pos_list[1])
                    ])
                }
                word_list.append(word_info)

    # TODO, check, if not good, just return Null
    # if larger than 0.5 of the column width more than 1/2 of the time

    return word_list


def pdf2txt(pdf_path):
    """
    export for indexing and heading extraction

    :param pdf_path:
    :return:
    """
    out_path = get_txt_path(pdf_path)
    if os.path.isfile(out_path):
        return
    from pdfxml.path_util import JAR_FOLDER
    from pdfxml.pipe_util import get_output
    print("Before pdf2txt position {}".format(os.getcwd()))

    cwd = os.getcwd()
    try:
        os.chdir(JAR_FOLDER)
        get_output(['java', '-jar', 'pdfbox-app-2.0.8.jar', 'ExtractText', pdf_path, out_path])
    except Exception as e:
        print e
    os.chdir(cwd)  # change back
    change2website_root()
    print("After pdf2txt position {}".format(os.getcwd()))


def get_txt_path(pdf_path):
    tmp_pdf_path = get_tmp_path(pdf_path)
    out_path = "{}.txt".format(tmp_pdf_path)
    return out_path


def pdf_extract_fontname2space(pdf_path, pid):
    fontname2space_list = {}
    check_export(pdf_path)
    page_char_path = get_page_char_path(pdf_path, pid)

    with open(page_char_path) as f:
        for line in f:
            if line.startswith("SPACE INFO:"):
                ws = line.strip().split("\t")
                fontname, space = ws[1], float(ws[2])
                if fontname not in fontname2space_list:
                    fontname2space_list[fontname] = []
                fontname2space_list[fontname].append(space)
    fontname2space = {}
    for fontname, space_list in fontname2space_list.items():
        fontname2space[fontname] = np.mean(space_list)
    return fontname2space


def get_pdf_page_size(pdf_path, pid=0):
    """
    NOTE: this should be the same as the function in the pdf_extract using pdfminer

    :param pdf_path:
    :param pid:
    :return:
    """
    check_export(pdf_path)

    page_char_path = get_page_char_path(pdf_path, pid)
    with open(page_char_path) as f:
        for line in f:
            if line.startswith("PDFINFO"):
                m = re.search(r"\(([\d\.]+), ([\d\.]+)\)", line)
                res_dict = {'width': float(m.group(1)), 'height': float(m.group(2))}

                return res_dict
    raise Exception("fail to get the PDFINFO")
