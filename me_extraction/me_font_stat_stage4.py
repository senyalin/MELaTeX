import re
import os
import traceback
import pdfxml.me_extraction.me_consts as ext_settings
from nltk.corpus import words, names
from nltk.stem.wordnet import WordNetLemmatizer
from pdfminer.layout import LTChar
from pdfxml.path_util import get_font_state_path, get_tmp_path
from pdfxml.file_util import dump_general, load_general
from pdfxml.loggers import me_extraction_logger
from pdfxml.doc_structure.struct_ignore_region import get_ignore_region
from pdfxml.pdf_util.tbl_fig_process import extract_tbl_fig_bbox
from pdfxml.pdf_util.clw_pipeline import clw_pdf_lines
from pdfxml.pdf_util.pdf_extract import get_page_num
from pdfxml.pdf_util.font_process import get_font_from_pdf, get_char_glyph
from pdfxml.pdf_util.char_process import char_list2bbox, char_list2str
from pdfxml.me_extraction.element_matching import out_citation, within_ref, structure_match, is_reference_head
from pdfxml.me_extraction.separate_math_text import check_is_math_LTChar, is_space_char
from pdfxml.me_extraction.me_consts import math_words, min_word_len_thres, special_nme_glyph_list
from pdfxml.pdf_util.layout_util import merge_bbox_list
from pdfxml.me_extraction.position_checking import check_word_subscript_exist
from pdfxml.sub_exp_matching.sequential_sub_exp_matching import SubExpMatching, sequential_sub_matching
from pdfxml.intervaltree_2d import IntervalTree2D
from pdfxml.me_extraction.post_expanding.expand_me_by_special_sym import get_me_nscs_by_expand_special_sym


# wl is for normal words, including the names
wl = set(words.words())
#wl.update(additional_words)
name_set = set(names.words())
name_set.update(['Dzmitry', 'Bahdanau', 'Jacobs', 'KyungHyun', 'Cho', 'Yoshua', 'Bengio'])
wl.update(name_set)
lower_wl = [w.lower() for w in wl]  # convert to lower case for normalization
wl.update(lower_wl)

wnl = WordNetLemmatizer()

nme_char_list = [
    u'\u2013'
]
"""
hold all the chars of ME or NME for a page.
This is for debugging purpose.
"""
EXPORT_WORD = True
nme_word_list = []
me_char_bbox_list = []
nme_char_bbox_list = []


def stage4_font_stat(pdf_path, refresh=False, debug=False):
    """
    The detail, check out the paper, or thesis

    :param pdf_path:
    :param refresh:
    :param debug:
    :return:
    """
    # load the experiment setting here.
    ext_settings.me_ext_default_setting()
    #print pdf_path

    font_stat_cache = "%s.me_vs_nme.fontcache.stage4.pkl"%(get_font_state_path(pdf_path))
    print "font_stat_cache: ", font_stat_cache

    if os.path.isfile(font_stat_cache) and not refresh:
        try:
            return load_general(font_stat_cache)
        except Exception as e:
            print font_stat_cache
            print traceback.format_exc()

    me_extraction_logger.info("Stage 4: conduct ME/NME font stat for file {}".format(pdf_path))
    me_font2count, nme_font2count, me_fontval2count, nme_fontval2count = {}, {}, {}, {}

    # Get the table Image, remove them
    tbl_fig_pid2bbox = extract_tbl_fig_bbox(pdf_path)

    exclude_pid2it2d = None
    if ext_settings.EXCLUDE_BY_SECTION:
        exclude_pid2it2d = get_ignore_region(pdf_path)
    # also keep the pid in order to remove the overlapping with existing
    pid2me_char_list_list = {}

    cross_page_info = {
        'met_ref_head': False
    }

    pn = get_page_num(pdf_path)
    for pid in range(pn):
        cross_page_info = stage4_process_page(
            pdf_path, pid,
            tbl_fig_pid2bbox, exclude_pid2it2d,
            nme_font2count, nme_fontval2count,
            me_font2count, me_fontval2count,
            pid2me_char_list_list,
            cross_page_info
        )

    # enable the sub_exp matching here
    if ext_settings.SUB_EXP_MATCH_V != ext_settings.SUB_EXP_MATCH_NO:
        me_extraction_logger.debug("Previous matched MEs")
        for pid, me_char_list_list in pid2me_char_list_list.items():
            for char_list in me_char_list_list:
                me_extraction_logger.debug(
                    "{}: {}".format(pid, char_list2str(char_list)))

        new_me_nscs_list = do_sub_exp_matching(pdf_path, pid2me_char_list_list, debug)
        for nscs in new_me_nscs_list:
            # another logic is that if it's alrady recongized,
            # the only purpose of the sub matching is to provide
            # enhanced probability when there is possibility of
            # conflicting.
            me_extraction_logger.debug(
                "Extra ME SUB Matching {}".format(char_list2str(nscs)))
            for c in nscs:
                add_me_char(c, me_font2count, me_fontval2count)

    expand_by_symbol(
        pdf_path, pid2me_char_list_list,
        me_font2count, me_fontval2count
    )

    res = {
        'me_font2count': me_font2count,
        'nme_font2count': nme_font2count,
        'me_fontval2count': me_fontval2count,
        'nme_fontval2count': nme_fontval2count
    }
    dump_general(res, font_stat_cache)

    return res


###################
# Common function #
###################
def expand_by_symbol(
        pdf_path,
        pid2me_char_list_list,
        me_font2count,
        me_fontval2count
        ):
    pn = get_page_num(pdf_path)
    if ext_settings.EXPAND_ME:
        for pid in range(pn):
            lines = internal_get_llines(None, pdf_path, pid)

            # NOTE the name is not very accurate
            existing_me_char_it2d = IntervalTree2D()
            # already added.

            for me_nscs in pid2me_char_list_list[pid]:
                existing_me_char_it2d.add_bbox_only(char_list2bbox(me_nscs))

            for li, line in enumerate(lines):
                expand_nscs_list = get_me_nscs_by_expand_special_sym(line)
                for new_nscs in expand_nscs_list:
                    new_nscs_bbox = char_list2bbox(new_nscs)
                    if existing_me_char_it2d.exist_overlap(new_nscs_bbox):
                        continue
                    me_extraction_logger.debug(
                        "Expand ME by Symbol {}".format(char_list2str(new_nscs)))
                    for c in new_nscs:
                        add_me_char(c, me_font2count, me_fontval2count)
                    pid2me_char_list_list[pid].append(new_nscs)


def is_struct_ignore_line(exclude_pid2it2d, pid, line):
    if exclude_pid2it2d is not None:
        line_bbox = char_list2bbox(line)
        if pid in exclude_pid2it2d:
            exclude_it2d = exclude_pid2it2d[pid]
            if exclude_it2d.exist_overlap(line_bbox):
                me_extraction_logger.debug(
                    "{} in ignored section".format(char_list2str(line)))
                return True
    return False


def do_sub_exp_matching(pdf_path, pid2me_char_list_list, debug=False):
    """

    :param pdf_path:
    :param pid2me_char_list_list:
        nscs list for ME
    :return:
    """
    sem = SubExpMatching(pid2me_char_list_list)
    pn = get_page_num(pdf_path)

    all_new_nscs_list = []
    for pid in range(pn):
        lines = internal_get_llines(None, pdf_path, pid)
        new_nscs_me_list = sequential_sub_matching(lines, sem, pid)
        all_new_nscs_list.extend(new_nscs_me_list)

    return all_new_nscs_list


def special_NME_checker(char_list, font):
    """
    check whether a char is NME or ME

    :param char_list:
    :param font:
    :return:
    """
    for char in char_list:
        if font is None:
            glyph_name = char.get_text()
        else:
            glyph_name = get_char_glyph(char, font)
        if glyph_name in special_nme_glyph_list:
            return True
    return False


def add_nme_char(c, nme_font2count, nme_fontval2count):
    if not isinstance(c, LTChar):
        return

    # for debugging purpose
    if ext_settings.debug:
        global nme_char_bbox_list
        nme_char_bbox_list.append(c.bbox)
    try:
        me_extraction_logger.debug(
            "ADD NME CHAR {}: {}".format(c.get_text().encode('utf-8'), c))
    except Exception as e:
        pass

    if not nme_font2count.has_key(c.fontname):
        nme_font2count[c.fontname] = 0
    nme_font2count[c.fontname] += 1

    p = (c.fontname, c.get_text())
    if not nme_fontval2count.has_key(p):
        nme_fontval2count[p] = 0
    nme_fontval2count[p] += 1


def add_me_char(c, me_font2count, me_fontval2count):
    """
    add chars to the statistics.
    :param c:
    :param me_font2count:
    :param me_fontval2count:
    :return:
    """
    if not isinstance(c, LTChar):
        return

    if ext_settings.debug:
        # for debugging purpose
        global me_char_bbox_list
        me_char_bbox_list.append(c.bbox)
    try:
        me_extraction_logger.debug(
            "ADD ME CHAR {}: {}".format(c.get_text().encode('utf-8', 'ignore'), c))
    except Exception as e:
        print e

    if not me_font2count.has_key(c.fontname):
        me_font2count[c.fontname] = 0
    me_font2count[c.fontname] += 1

    p = (c.fontname, c.get_text())
    if not me_fontval2count.has_key(p):
        me_fontval2count[p] = 0
    me_fontval2count[p] += 1


def internal_nme_assessment(word_info_dict, line, font,
                            ref_label, cit_label, struct_label,
                            nme_font2count, nme_fontval2count,
                            me_font2count, me_fontval2count,
                            me_char_list_list,
                            exclude_it2d
                            ):
    """
    word_info = {
        'word': word, 'lineidx': li,
        'range': [beg_idx, i], 'plain': 0}

    :param word_info_dict:
    :param line:
    :param font:
    :param ref_label:
    :param cit_label:
    :param struct_label:
    :param nme_font2count:
    :param nme_fontval2count:
    :param me_font2count:
    :param me_fontval2count:
    :return:
    """
    beg_idx = word_info_dict['range'][0]
    i = word_info_dict['range'][1]
    word = word_info_dict['word']

    # NOTE, added March. 15
    # in some section such as abs or reference
    # not to be included
    if exclude_it2d is not None:
        for j in range(beg_idx, i):
            if isinstance(line[j], LTChar) and \
                    exclude_it2d.exist_overlap(line[j].bbox):
                # do not proceed if overlap with something.
                return

    # if meet any math symbol here
    # check current word only
    word_with_me = False
    for j in range(beg_idx, i):
        if isinstance(line[j], LTChar) and check_is_math_LTChar(line[j], font):
            word_with_me = True
            break
    try:
        me_extraction_logger.debug("Testing Word {}".format(word.encode('utf-8')))
    except Exception as e:
        me_extraction_logger.debug(str(e))

    # also check some NME Indicator
    # if bullet, hyphen
    special_nme = special_NME_checker([line[j] for j in range(beg_idx, i)], font)

    # numbers possible as heading

    # in ref, as nme
    is_within_ref = False
    for j in range(beg_idx, i):
        if ref_label[j]:
            is_within_ref = True
            break

    # if the word match [\d]
    word_as_citation = False
    for j in range(beg_idx, i):
        if cit_label[j]:
            word_as_citation = True
            break

    # struct part
    word_as_struct = False
    for j in range(beg_idx, i):
        if struct_label[j]:
            word_as_struct = True
            break

    # check rule 2
    if word_as_struct:  # nme
        me_extraction_logger.debug("Meet Within structure {}".format(word.encode('utf-8')))
        for j in range(beg_idx, i):
            add_nme_char(line[j], nme_font2count, nme_fontval2count)
    elif is_within_ref:  # nme
        me_extraction_logger.debug("Meet Within pub ref {}".format(word.encode('utf-8')))
        for j in range(beg_idx, i):
            add_nme_char(line[j], nme_font2count, nme_fontval2count)
    elif special_nme:
        me_extraction_logger.debug("Meet Special NME {}".format(word.encode('utf-8')))
        for j in range(beg_idx, i):
            add_nme_char(line[j], nme_font2count, nme_fontval2count)
    elif word_as_citation:
        me_extraction_logger.debug("Meet Citation {}".format(word.encode("utf-8")))
        for j in range(beg_idx, i):
            add_nme_char(line[j], nme_font2count, nme_fontval2count)
    elif word_with_me:
        try:
            me_extraction_logger.debug("Meet ME Word {}".format(word.encode('utf-8')))
        except Exception as e:
            print e

        for j in range(beg_idx, i):
            add_me_char(line[j], me_font2count, me_fontval2count)
        me_char_list_list.append(line[beg_idx:i])


def stage4_process_page(
        pdf_path, pid,
        tbl_fig_pid2bbox, exclude_pid2it2d,
        nme_font2count, nme_fontval2count, me_font2count, me_fontval2count,
        pid2me_char_list_list,
        cross_page_info
        ):
    """
    :param me_fontval2count:
    :param me_font2count:
    :param pid2me_char_list_list:
    :param nme_fontval2count:
    :param nme_font2count:
    :param pdf_path:
    :param pid:
    :param tbl_fig_pid2bbox:
    :param exclude_pid2it2d:
    :return:
    """
    met_ref_head = cross_page_info['met_ref_head']

    # list of char_list of MEs to match other sub MEs.
    me_char_list_list = []

    # TODO, remove: nme_word_list = []
    # TODO, why do I need this font_dict
    # to map the char to their glyph names?
    font_dict = get_font_from_pdf(pdf_path, pid)

    lines = internal_get_llines(None, pdf_path, pid)
    tbl_fig_bbox_list = []
    if pid in tbl_fig_pid2bbox:
        tbl_fig_bbox_list = tbl_fig_pid2bbox[pid]

    word_info_list = []
    line_labels = [0] * len(lines)
    for li, line in enumerate(lines):
        if is_struct_ignore_line(exclude_pid2it2d, pid, line):  # struct such as abs and ref
            continue

        # within_ref
        ref_label = within_ref(line)
        cit_label = out_citation(line)
        struct_label = structure_match(line)

        line_label, beg_idx = 0, 0
        with_math_symbol_or_word, with_non_math_word = False, False  # for whole line, of IME assessment

        line_str = char_list2str(line)

        if is_reference_head(line_str):
            met_ref_head = True
        if met_ref_head:
            # just add as NME
            # TODO, if could differentiate reference with appendix
            # TODO enable this function after better section recogn
            pass

        for i, char in enumerate(line):
            # NOTE, does not consider the word that occur in two lines, wrapped
            if isinstance(char, LTChar):
                is_math_char = check_is_math_LTChar(char, font_dict)
                if is_math_char:
                    with_math_symbol_or_word = True
                me_extraction_logger.debug(
                    "Check Math Char {} {}".format(char, is_math_char))

            if is_space_char(char):
                word = ""
                for j in range(beg_idx, i):
                    try:
                        word += line[j].get_text()
                    except Exception as e:
                        print 'fxxx coding issue'
                        print e

                # remove the last symbol
                # TODO, also the dagger after the names.
                if word.endswith(',') or word.endswith('.'):
                    word = word[:-1]

                word_info = {
                    'word': word, 'lineidx': li,
                    'range': [beg_idx, i], 'plain': 0}
                word_info_list.append(word_info)

                # organized code for NME assessment
                exclude_it2d = None
                if exclude_pid2it2d is not None and pid in exclude_pid2it2d:
                    exclude_it2d = exclude_pid2it2d[pid]
                internal_nme_assessment(
                    word_info, line, font_dict, ref_label, cit_label, struct_label,
                    nme_font2count, nme_fontval2count, me_font2count, me_fontval2count,
                    me_char_list_list, exclude_it2d)

                word = word.lower().strip()
                s_word = word
                v_word = word
                try:
                    s_word = wnl.lemmatize(word, 'n')
                except Exception as e:
                    print e

                try:
                    v_word = wnl.lemmatize(word, 'v')
                except Exception as e:
                    print e

                is_nlp_word = (word in wl or s_word in wl or v_word in wl)
                if ext_settings.debug:
                    if word == 'summation':
                        pass
                    me_extraction_logger.debug( "Org: {}, S: {}, V: {}, as nlp: {}".format(
                        word, s_word, v_word, is_nlp_word ))
                nme_char_exist = False
                for nme_c in nme_char_list:
                    try:
                        if nme_c in word:
                            nme_char_exist = True
                    except Exception as e:
                        me_extraction_logger.error(traceback.format_exc())

                tmp_char_list = []
                for j in range(beg_idx, i):
                    if isinstance(line[j], LTChar):
                        tmp_char_list.append(line[j])

                in_fig_tbl = False
                if len(tmp_char_list) > 0:
                    word_bbox = merge_bbox_list([c.bbox for c in tmp_char_list])
                    for tmp_bbox in tbl_fig_bbox_list:
                        if tmp_bbox.contain_bbox(word_bbox):
                            me_extraction_logger.debug(
                                "In Fig/Tbl for Word {}".format(word.encode('utf-8')))
                            in_fig_tbl = True

                if word in math_words:
                    with_math_symbol_or_word = True
                if len(word) > min_word_len_thres and is_nlp_word:
                    with_non_math_word = True

                if in_fig_tbl:
                    # put larger priory
                    for j in range(beg_idx, i):
                        add_nme_char(line[j], nme_font2count, nme_fontval2count)

                elif len(word) > min_word_len_thres and is_nlp_word:
                    with_non_math_word = True

                    for j in range(beg_idx, i):
                        add_nme_char(line[j], nme_font2count, nme_fontval2count)
                    if ext_settings.debug:
                        me_extraction_logger.debug("NME {}".format(word))
                    word_info_list[-1]['plain'] = 1
                elif ext_settings.ENABLE_SINGLE_CHAR and len(word) == 1 and word not in ['A', 'a']:
                    # TODO, there might be an error introduced here.
                    # [I, ] and punctuations should also be ignored
                    for j in range(beg_idx, i):
                        add_nme_char(line[j], me_font2count, me_fontval2count)
                    if ext_settings.debug:
                        me_extraction_logger.debug("Single Word ME {}".format(word))
                elif nme_char_exist:
                    # This is quite arbitary, put with low prioirty
                    me_extraction_logger.debug(
                        "Meet NME Char for {}".format(word.encode('utf-8')))
                    for j in range(beg_idx, i):
                        add_nme_char(line[j], nme_font2count, nme_fontval2count)
                else:  # TODO  nothing
                    pass

                # check script here, as ME
                if not is_nlp_word and ext_settings.SUBSCRIPT_CHECK:
                    # but it might not be strong enough
                    char_list = [line[j] for j in range(beg_idx, i)]
                    sub_exist = check_word_subscript_exist(char_list)
                    if sub_exist:
                        # logging
                        tmp_word_str = "".join([c.get_text() for c in char_list])
                        me_extraction_logger.debug("ME FOUND Subscript: {}".format(
                            tmp_word_str.encode('utf-8')
                        ))

                        for j in range(beg_idx, i):
                            add_me_char(line[j], me_font2count, me_fontval2count)
                        me_char_list_list.append(line[beg_idx:i])

                # update at the end due to the need to use the beg_idx
                beg_idx = i + 1

        if ext_settings.debug:
            tmp_str = char_list2str(line)
            me_extraction_logger.debug("The tested line {}, with_math {}, without {}".format(
                tmp_str.encode('utf-8'), with_math_symbol_or_word, with_non_math_word
            ))

        if with_math_symbol_or_word and (not with_non_math_word):
            # is IME here
            line_label = 1
            me_extraction_logger.debug(
                "Meet IME Line {}".format(char_list2str(line)))
            for char in line:
                add_me_char(char, me_font2count, me_fontval2count)

            # for sub-exp matching
            me_char_list_list.append(line)
        line_labels[li] = line_label

    # neighbour based Abbreviation matching
    # label as only capatialized
    if not ext_settings.DISABLE_ABBR_NME:
        cap_label_list = []
        for i, wi in enumerate(word_info_list):
            if len(wi['word']) > 0 and wi['word'][-1] == 's':
                w = wi['word'][:-1]
                if len(w) > 1 and re.match(r'[A-Z]+$', w):
                    cap_label_list.append(1)
                else:
                    cap_label_list.append(0)
            else:
                if len(wi['word']) > 1 and re.match(r'[A-Z]+$', wi['word']):
                    cap_label_list.append(1)
                else:
                    cap_label_list.append(0)

        for i in range(1, len(word_info_list) - 1):
            prev_match = word_info_list[i - 1]['word'].lower() in wl
            next_match = word_info_list[i + 1]['word'].lower() in wl
            me_extraction_logger.debug(
                "{} {} {} {} {}".format(
                    word_info_list[i - 1]['word'].encode('utf-8'),
                    word_info_list[i]['word'].encode('utf-8'), prev_match,
                    word_info_list[i + 1]['word'].encode('utf-8'), next_match
                )
            )

            prev_word = word_info_list[i - 1]['word'].lower()
            next_word = word_info_list[i + 1]['word'].lower()
            if cap_label_list[i] and (prev_word in wl or next_word in wl):
                me_extraction_logger.debug("Meet abbreviation".format(word_info_list[i]['word']))
                for j in range(word_info_list[i]['range'][0], word_info_list[i]['range'][1]):
                    li = word_info_list[i]['lineidx']
                    add_nme_char(lines[li][j], nme_font2count, nme_fontval2count)
    pid2me_char_list_list[pid] = me_char_list_list

    return {
        'met_ref_head': met_ref_head
    }


def internal_get_llines(prefix, pdf_path, pid):
    """
    :param prefix:
    :param pdf_path:
    :param pid:
    :return:
    """
    from pdfxml.file_util import load_serialization, dump_serialization
    tmp_prefix = get_tmp_path(pdf_path)
    cache_path = "{}.me_extraction_line.{}.pkl".format(tmp_prefix, pid)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    lines = clw_pdf_lines(pdf_path, pid)

    dump_serialization(lines, cache_path)
    return lines


if __name__ == "__main__":
    #pdf_path = "C:/Users/senyalin/Dropbox/test/pdfxml/test/lda2vec.pdf"
    pdf_path = "C:/Users/user/Dropbox/test/pdfxml/test/lda2vec.pdf"
    print stage4_font_stat(pdf_path)