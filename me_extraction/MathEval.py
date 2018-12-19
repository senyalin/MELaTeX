# -*- coding: utf-8 -*-
#################################################################################
#Program    :   MathEval.py                                                     #
#Version    :   20111123 (date of last modification)                            #
#Author     :   HuXuan (huxuan@icst.pku.edu.cn)                                 #
#               LinXiaoYan (lingxiaoyan@pku.edu.cn)                             #
#Usage      :                                                                   #
#   0)  Make sure your script is the latest version                             #
#   1)  Copy Ground Truth file in the folder 'GT'                               #
#       (the folder name can be changed by modify the source code)              #
#   2)  Copy Machine Detection file in the folder 'MD'                          #
#       (the folder name can also be changed)                                   #
#   3)  Make folder 'GT', folder 'MD' and 'MathEval.py' under the same folder   #
#   4)  Run the python script via command line or just double click it          #
#   5)  The result will be shown in 'MathEval.csv'                              #
#       Time used can be seen in the command line                               #
                                                                                #
#Some variable abbreviation:                                                    #
#   E: EmbeddedFormula, I: IsolatedFormula                                      #
#   l: left, r:right, t: top, b:bottom                                          #
#   p: path, dir: directory                                                     #
#   gt: Ground Truth, md: Machine Detection                                     #
#   cor: Correct, mis: Miss, fal: False, par: Partial                           #
#   exp: Expand, pae: Partial&Expand, mer: Merge, spl: Split                    #
#################################################################################

import struct
import string
import xml.dom.minidom


def hexlongbits2double(str):
    """docstring for hexlongbits2double
    Summary:
        Conver the longbits in hex to double

        Q is the unsigned long long
        d is double
    Parameter:
        [input]     str     -   string of the longbits in hex
        [return]    the double result of the convert
    """
    return struct.unpack('d', struct.pack('Q', int(str, 16)))[0]


def bbox2rect(bbox):
    """docstring for bbox2rect
    Summary:
        convert bbox string (in the xml file) to rect and calculate the area at the same time
    Parameter:
        [input]     bbox    -   the bbox string
        [return]    a dict with 'area' and 'rect' keys to indicate each
    """
    rect = {}
    rect['l'] = hexlongbits2double(bbox[0])
    rect['t'] = hexlongbits2double(bbox[1])
    rect['r'] = hexlongbits2double(bbox[2])
    rect['b'] = hexlongbits2double(bbox[3])
    area = (rect['r'] - rect['l']) * (rect['t'] - rect['b'])
    return {'area':area, 'rect':rect}


def parse_xml(p_xml):
    """docstring for parse_xml
    Summary:
        Parse the xml just handle some exceptions
    Parameter:
        [input]     p_xml   -   path of the xml file
        [returm]    flag    -   boolean to indicate wheather parsed successfully
        [return]    xmldoc  -   xml document variable of the xml file, None for failing to parse
    """
    flag = True
    try:
        xmldoc = xml.dom.minidom.parse(p_xml)
    except:
        try:
            # Try to replace unprintable chars and parse via string
            f = file(p_xml, 'rb')
            s = f.read()
            f.close()

            ss = s.translate(None, string.printable)
            s = s.translate(None, ss)

            xmldoc = xml.dom.minidom.parseString(s)
        except:
            xmldoc = None
            flag = False
    return flag, xmldoc


def get_me_str(f_node):
    """
    given a formula node,
    get the Char children,
    and get the text
    """

    s = ""
    for c in f_node.getElementsByTagName('Char'):
        s += c.getAttribute('Text')
    #print s
    return s


def get_info(p_xml):
    """docstring for get_info
    Summary:
        Get all needed info from xml file
    Parameter:
        [input]     p_xml       -   path of xml file
        [return]    formulas    -   needed infomation of all formulas
    """
    #print "load ground truth from ", p_xml
    formulas = []
    flag, xmldoc = parse_xml(p_xml)
    if flag:

        # foreach all the Embedded Formulas
        for i in xmldoc.getElementsByTagName('EmbeddedFormula'):
            #print i
            formula = {}
            formula.update(bbox2rect(i.getAttribute('BBox').split())) # update rect and area info
            formula['type'] = 'E' # add formula type info
            formula['str'] = get_me_str(i)
            if formula['area'] > 0:
                formulas.append(formula)

        # foreach all the Isolated Formulas
        for i in xmldoc.getElementsByTagName('IsolatedFormula'):
            #print i
            formula = {}
            formula.update(bbox2rect(i.getAttribute('BBox').split())) # update rect and area info
            formula['type'] = 'I' # add formula type info
            formula['str'] = get_me_str(i)

            if formula['area'] > 0:
                formulas.append(formula)

    return flag, formulas


if __name__ == '__main__':
    pass