"""
The elements here refer to the document structures
"""

import re
import unittest

from pdfminer.layout import LTChar
from pdfxml.loggers import me_extraction_logger


def get_fill_space_str(char_list):
    """
    get the string with the space (LtAnno) and longer than 1 char filled as empty
    not sure why: longer than 1 char filled as empty

    :param char_list:
    :return:
    """
    tmp_str = ""
    for char in char_list:
        if isinstance(char, LTChar):
            text = char.get_text()
            try:
                text.encode('utf-8')
                if len(text) > 1:
                    tmp_str += " "
                else:
                    tmp_str += text
            except Exception as e:
                tmp_str += " "

        else:
            tmp_str += " "
    return tmp_str


def out_citation_str(tmp_str):
    'statisticalexperimentaldesign.(Montgomery(1984)isa'
    cit_reg1 = r"\[\d{1,3}\]"
    cit_reg2 = r"\[\d{1,3}([ ]*,[ ]*\d{1,3})*\]"
    cit_reg3 = r"\((18|19|20)\d\d\)"
    cit_reg4 = r"\([^1-9\(\)]*\d\d\d\d\)"
    cit_reg5 = r"([A-Z][a-z]*?[ ]*et[ ]*al.[ ]*,[ ]*(18|19|20)\d\d[ ab])"
    # (Abz et al. 1111)
    cit_reg6 = r"([A-Z][a-z]*[ ]*et[ ]*al[ ]*\.[ ]*\((18|19|20)\d{2}[ ab]*\))"
    # Abz et al. (1111)
    cit_reg7 = r"([A-Z][a-z]*[ ]*et[ ]*al[ ]*\.)"
    # only matching the names
    cit_reg8 = r"[A-Z][a-z]*?[ ]*\((18|19|20)\d\d\)"
    cit_reg9 = r"\d{2,4}-\d{2,4}"  # citation number matching

    cit_reg_list = [
        cit_reg1, cit_reg2,
        cit_reg3, cit_reg4, cit_reg5, cit_reg6, cit_reg7,
        cit_reg8, cit_reg9
    ]

    me_extraction_logger.debug("test citation {}".format(tmp_str.encode('utf-8')))

    label = [0]*len(tmp_str)
    for cit_idx, cit_reg in enumerate(cit_reg_list):
        if re.search(cit_reg, tmp_str):
            for m in re.finditer(cit_reg, tmp_str):
                me_extraction_logger.debug("match citation {} {}".format(cit_idx, m))
                for i in range(m.start(), m.end()):
                    label[i] = 1
    return label


def out_citation(char_list):
    """
    out citation means cross paper reference

    try to match citation
    http://stackoverflow.com/questions/4320958/regular-expression-for-recognizing-in-text-citations

    :param char_list:
    :return:
    """
    tmp_str = get_fill_space_str(char_list)
    return out_citation_str(tmp_str)


def within_ref(char_list):
    """
    reference to element in this current document
    figure,
    table, form,
    equation, eqn., formula,

    TODO, create test case db for this
    Fig. 1
    Figure 1
    formula (39)

    """
    tmp_str = get_fill_space_str(char_list)
    me_extraction_logger.debug("test with reference: {}".format(tmp_str.encode('utf-8', 'ignore')))

    # try to match all these options
    fig_reg = r"(figure|fig.)[ ]*\d+(\.\d+)*[ ]*(\([a-zA-Z]\)|\[[a-zA-Z]\])*"
    tbl_reg = r"(table|tbl.|tab|tlb|form)[ ]*\d+(\.\d+)*[ ]*(\([a-zA-Z]\)|\[[a-zA-Z]\])*"
    eq_reg = r"(equation|eqn.|eq.|formula)[ ]*(\d+(\.\d+)*|\(\d+(\.\d+)*\)|\d+|\(\d+\))"
    # match the long one firstly

    # assumeing only one types of match
    label = [0]*len(char_list)
    # label 0 is normal , 1, 2, 3 for fig, table, and equation
    if re.search(fig_reg, tmp_str, re.I):
        for m_fig in re.finditer(fig_reg, tmp_str, re.I):
            me_extraction_logger.info(
                "Match fig {} {} {}".format(m_fig.group(0), m_fig.start(), m_fig.end())
            )
            for i in range(m_fig.start(), m_fig.end()):
                label[i] = 1
    elif re.search(tbl_reg, tmp_str, re.I):
        for m_tbl in re.finditer(tbl_reg, tmp_str, re.I):
            me_extraction_logger.info(
                "Match tbl {} {} {}".format(m_tbl.group(0), m_tbl.start(), m_tbl.end())
            )
            for i in range(m_tbl.start(), m_tbl.end()):
                label[i] = 2
    elif re.search(eq_reg, tmp_str, re.I):
        for m_eq in re.finditer(eq_reg, tmp_str, re.I):
            me_extraction_logger.info(
                "Match eq {} {} {}".format(m_eq.group(0), m_eq.start(), m_eq.end())
            )
            for i in range(m_eq.start(), m_eq.end()):
                label[i] = 3
    else:
        pass

    return label


def structure_match(char_list):
    """
    with in paper reference

    example:
    Theorem/Definition/Example/Collary \d+(\.\d+)*
    Chapter/Section \d+
    ^\d+(\.\d+)* number in the beginning

    :param char_list:
    :return:
    """
    tmp_str = get_fill_space_str(char_list)
    me_extraction_logger.debug(
        "Try to extract structure from sent {}".format(tmp_str.encode('utf-8'))
    )

    block_reg = r"(theorem|definition|example|collary)[ ]*\d+(\.\d+)*"
    #u'fi' # the glyph design problem...
    struct_reg = r"(chapter|section)[ ]*\d+(\.\d+)*"
    email_reg = r"\S+@\S+\.\S+"
    url_reg = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    reg_list = [
        block_reg, struct_reg, email_reg, url_reg
    ]

    label = [0]*len(char_list)
    for reg in reg_list:
        if re.search(reg, tmp_str, re.I):
            for m in re.finditer(reg, tmp_str, re.I):
                for i in range(m.start(), m.end()):
                    label[i] = 1
    """
        if re.search(block_reg, tmp_str, re.I):
        for m_block in re.finditer(block_reg, tmp_str, re.I):
            me_extraction_logger.info("Match block {}".format( m_block.group(0) ))
            for i in range(m_block.start(), m_block.end()):
                label[i] = 1
    elif re.search(struct_reg, tmp_str, re.I):
        for m_struct in re.finditer(struct_reg, tmp_str, re.I):
            me_extraction_logger.info("Match struct {}".format( m_struct.group(0) ))
            for i in range(m_struct.start(), m_struct.end()):
                label[i] = 1
    else:
        pass
    """

    return label


def is_reference_head(line):
    if re.search("^[ ]*\d(\.\d+)*[ ]*references[ ]*$", line, re.I) or \
            re.search("^[ ]*(\d+\.)*[ ]*references[ ]*$", line, re.I) or \
            re.search("^[ ]*references[ ]*$", line, re.I):
        return True
    else:
        return False


def test_is_reference_head():
    assert is_reference_head("References") == True
    assert is_reference_head("7. References") == True
    assert is_reference_head("they References") == False
    assert is_reference_head("7.1 References") == True


if __name__ == "__main__":
    unittest.main()
