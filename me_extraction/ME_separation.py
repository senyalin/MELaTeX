"""
Detection of isolated Mathematical expression
1. if the line don't have word
2. if the line have some math element
"""
import os
import shutil
import time
from nltk.corpus import words
from nltk.stem.wordnet import WordNetLemmatizer
from pdfminer.layout import LTChar

import pdfxml.me_extraction.me_consts as ext_settings
from pdfxml.me_extraction.EME_separation_font_stat import create_me_font_condprob
from pdfxml.me_extraction.EME_separation_font_val_stat import create_me_font_val_condprob, check_me_font_val, \
    get_me_nme_log_prob_font_val
from pdfxml.me_extraction.MathEval import get_info
from pdfxml.path_util import get_xml_path, get_eme_path, get_ime_path
from pdfxml.me_extraction.me_consts import CLW_FEB, CLW_OLD
from pdfxml.me_extraction.me_consts import additional_words
from pdfxml.me_extraction.me_font_stat_stage4 import stage4_font_stat, internal_get_llines
from pdfxml.me_extraction.separate_math_text import check_is_math_LTChar, \
    is_space_char  # TODO, only extract the useful util here
from pdfxml.me_extraction.serialization import export_xml
from pdfxml.loggers import me_extraction_error_logger, me_extraction_logger
from pdfxml.profiling import get_global_duration_recorder

from pdfxml.pdf_util.char_process import char_list2str, char_list2bbox
from pdfxml.path_util import get_tmp_path
from pdfxml.pdf_util.font_process import get_font_from_pdf
from pdfxml.pdf_util.layout_util import char_in_bbox_list, bbox_half_overlap_list
from pdfxml.pdf_util.pdf_extract import get_page_num
from pdfxml.pdf_util.pdfbox_wrapper import export_exact_position
from pdfxml.pdf_util.word_seg_process import char_list2char_list_list
from pdfxml.file_util import get_file_name_prefix

duration_recorder = get_global_duration_recorder()


######################
#   IME Separation   #
######################
def assess_ime(pdf_path, pid=0, xml_out_path=None, ignore_exist=False):
    """
    # IME [3]

    With math symbol and without non-math words

    Return:
        xml_out_path: output the boundary file
    """
    tmp_path = get_tmp_path(pdf_path)
    ret_info_dict = {}
    if xml_out_path and os.path.isfile(xml_out_path) and (not ignore_exist):
        return {}

    from pdfxml.me_extraction.me_consts import math_words
    t = time.time()
    # common resource loader
    wl = set(words.words())
    wl.update(additional_words)
    wnl = WordNetLemmatizer()
    d = time.time()-t
    ret_info_dict['resource_time'] = d

    t = time.time()
    # layout analysis
    font = get_font_from_pdf(pdf_path, pid)
    #font = None
    prefix = pdf_path[pdf_path.rindex("/") + 1:-4]
    lines = internal_get_llines(prefix, pdf_path, pid)

    d = time.time()-t
    ret_info_dict['layout_time'] = d

    # IME assessment core
    t = time.time()
    line_labels = [0]*len(lines)
    for li, line in enumerate(lines):
        line_label = 0
        beg_idx = 0
        with_math_symbol_or_word = False
        with_non_math_word = False
        for i, char in enumerate(line):
            if isinstance(char, LTChar):
                if check_is_math_LTChar(char, font):
                    me_extraction_logger.debug("Char {} as Math".format(char))
                    with_math_symbol_or_word = True

            if is_space_char(char):
                word = ""
                for j in range(beg_idx, i):
                    if j == i-1 and line[j].get_text() in [',', '.', 'period', 'comma']:
                        continue

                    # for word checking, only work on the alpha beta
                    tmp_text = line[j].get_text()
                    if len(tmp_text) != 1:
                        tmp_text = " "

                    word += tmp_text
                beg_idx = i+1
                word = word.lower().strip()

                # move to above, and use glyph name to match
                #if word.endswith(',') or word.endswith('.'):
                #    word = word[:-1]

                # print check word
                s_word, v_word = "", ""
                try:
                    s_word = wnl.lemmatize(word, 'n')
                    v_word = word
                    v_word = wnl.lemmatize(word, 'v')
                except Exception as e:
                    me_extraction_error_logger.error("Error checking the word as noun or verb")

                if word in math_words:
                    me_extraction_logger.debug("Math Word {}".format(word))
                    with_math_symbol_or_word = True
                elif len(word) > 2 and (word in wl or s_word in wl or v_word in wl):
                    me_extraction_logger.debug("Plain Word {}".format(word))
                    with_non_math_word = True
                else:
                    pass

        # debug for line, with ME or not
        tmp_line_str = char_list2str(line, ', ')
        me_extraction_logger.debug(tmp_line_str)
        me_extraction_logger.debug("with math {}, with word {}".format(
            with_math_symbol_or_word,
            with_non_math_word
        ))
        if with_math_symbol_or_word and (not with_non_math_word):
            me_extraction_logger.debug("MATHLINE")
            line_label = 1
        line_labels[li] = line_label
    d = time.time()-t
    ret_info_dict['core_time'] = d

    if not xml_out_path:
        for li, line in enumerate(lines):
            if line_labels[li]:
                tmp_str = ''.join([char.get_text() for char in line if isinstance(char, LTChar)])
                print tmp_str.encode("utf-8")

    # export for evaluation
    page_info = {}
    page_info['pid'] = pid
    page_info['ilist'] = []
    page_info['elist'] = []

    # create bbox for each ME
    for li, line in enumerate(lines):
        if line_labels[li]:
            visible_char_list = [char for char in line if isinstance(char, LTChar)]
            char_list2str(visible_char_list)
            page_info['ilist'].append(line)

    t = time.time()
    if xml_out_path:
        export_xml(page_info, xml_out_path, pdf_path, pid)
    d = time.time()-t
    ret_info_dict['io_time'] = d
    return ret_info_dict


def extract_ime(pdf_path):
    # IME [1]
    """
    given a pdf path, extract the ime for each page
    """
    xml_path = get_xml_path(pdf_path)
    pn = get_page_num(pdf_path)

    if not ext_settings.ME_ANALYSIS_PARALLEL:
        for pid in range(pn):
            # prepare the path

            xml_out_path = get_ime_path(pdf_path, pid)
            if not os.path.isfile(xml_out_path):
                assess_ime(pdf_path, pid, xml_out_path)
    else:
        from multiprocessing import Process
        process_list = []
        for pid in range(pn):
            p = Process(target=assess_ime, args=(pdf_path, pid, get_ime_path(pdf_path, pid)))
            process_list.append(p)
            p.start()
        for p in process_list:
            p.join()

        #Parallel(n_jobs=PARALLEL_SIZE)(
        #    delayed(assess_ime)(pdf_path, pid, get_ime_path(pdf_path, pid)) for pid in range(pn)
        #)


######################
#   EME Separation   #
######################
def eme_merger(lines, me_chars, ime_bbox_list):
    """
    1. if overlap with IME, ignore
    2. if consecutive as EME, merge them all

    3. a bit complex, if seperated by comma, dot only, should also merge them

    :param lines:
    :param me_chars:
    :param ime_bbox_list:
    :return:
    """
    eme_list = []
    for li, line in enumerate(lines):
        i = 0
        while i < len(line):
            char = line[i]

            if is_space_char(char):  # if space , continue
                i += 1
                continue
            if char_in_bbox_list(char, ime_bbox_list):  # IME ignore
                i += 1
                continue

            if char in me_chars:  # met a begin position
                end_idx = i+1
                # try to find the ending position
                # skip none LTChar, comma, period, ',', '.'
                # also pay attention to the last element boundary condition
                while end_idx < len(line):
                    if not isinstance(line[end_idx], LTChar):
                        end_idx += 1
                    elif line[end_idx] in me_chars:
                        end_idx += 1
                    elif line[end_idx].get_text() in [',', '.', 'comma', 'period']:
                        end_idx += 1
                    else:
                        break
                # strip the ending element not as ME
                if end_idx == len(line):
                    end_idx -= 1
                while end_idx > i:
                    if line[end_idx] not in me_chars:
                        end_idx -= 1
                    else:
                        break
                tmp_chars = [line[j] for j in range(i, end_idx+1) if isinstance(line[j], LTChar)]
                eme_list.append(tmp_chars)
                i = end_idx+1
            else:
                i += 1

    return eme_list


def EME_font_stat_pipeline(
        pdf_path, pid,
        eme_export_path=None, prev_page_info={}
        ):
    """
    for each word, compare the probability
    :param pdf_path:
    :param pid:
    :param eme_export_path:
    :param stage:
    :param refresh_font_stat:
    :param condprob_type: font, font-val
    :param word_export_path:
    :param refresh:
    :return:
    """
    #print "NOTE force EME extraction to be false"
    #ext_settings.LANG_MODEL = False
    #SEQ_ME_MERGER = False

    ret_info_dict, t = {}, time.time()  # assign value and get the current time
    font_stat_dict = stage4_font_stat(pdf_path)
    me_font_condprob = create_me_font_condprob(font_stat_dict) # the conditional prob
    font_val_condprob = create_me_font_val_condprob(font_stat_dict)
    d = time.time()-t

    ret_info_dict['stat_time'], t = d, time.time()
    font = get_font_from_pdf(pdf_path, pid)

    prefix = pdf_path[pdf_path.rindex("/") + 1:-4]
    lines = internal_get_llines(prefix, pdf_path, pid)

    d = time.time()-t
    ret_info_dict['layout_time'], t = d, time.time()

    # the loaded IME play two roles here:
    # * another rule here, if the word is part of an IME line, then also good
    # * find connected EME, should not overlap with IME
    xml_path = get_xml_path(pdf_path)
    ime_res_path = "{}.ime.{}.xml".format(xml_path, pid)
    if not os.path.isfile(ime_res_path):
        assess_ime(pdf_path, pid, ime_res_path)

    gt_flag, gt_me_list = get_info(ime_res_path)
    gt_ime_list = [gt_me for gt_me in gt_me_list if gt_me['type'] == 'I']

    ime_bbox_list = [
        [gt_ime['rect']['l'], gt_ime['rect']['b'], gt_ime['rect']['r'], gt_ime['rect']['t']] \
        for gt_ime in gt_ime_list
    ]

    d = time.time()-t
    ret_info_dict['ime_time'] = d

    t = time.time()
    me_chars = set()

    references_met = False  # TODO, the refer might cover many pages
    if 'references_met' in prev_page_info:
        references_met = True
        #return

    eme_list = []
    word_class_list = []
    nscs_label_list_list = []

    for li, line in enumerate(lines):
        nscs_label_list = []
        beg_idx = 0

        # TODO, reference has a regex later
        # at the level of line
        tmp_str = char_list2str(line)

        from pdfxml.me_extraction.element_matching import is_reference_head
        if is_reference_head(tmp_str):
            references_met = True
            ret_info_dict['references_met'] = True
            break

        line_bbox = char_list2bbox(line)
        if bbox_half_overlap_list(line_bbox, ime_bbox_list):
            if ext_settings.debug:
                me_extraction_logger.debug("Line {} as IME".format(char_list2str(line)))
            continue

        nscs_list = char_list2char_list_list(line)
        nscs_str_list = [char_list2str(nscs) for nscs in nscs_list]
        me_log_prob_list = []
        nme_log_prob_list = []
        for nscs in nscs_list:
            nscs_pred = nscs
            if nscs[-1].get_text() in [',', '.']:
                nscs_pred = nscs[:-1]

            # only use the font-val pair to make inferecen now
            is_me = check_me_font_val(
                nscs_pred, font_val_condprob, me_font_condprob, font, debug=ext_settings.debug)
            me_prob, nme_prob = get_me_nme_log_prob_font_val(
                nscs_pred, font_val_condprob, me_font_condprob, font, debug=ext_settings.debug)
            if is_me and ext_settings.debug:
                me_extraction_logger.debug("check me font val ME")
            me_log_prob_list.append(me_prob)
            nme_log_prob_list.append(nme_prob)

            if is_me:
                # print sth here
                tmp_str = char_list2str(nscs)
                if ext_settings.debug:
                    me_extraction_logger.debug("me chunk {}".format(tmp_str.encode('utf-8')))
                me_chars.update([c for c in nscs if isinstance(c, LTChar)])
                word_class_list.append((nscs, 1))
                nscs_label_list.append((nscs, 1))
            else:
                word_class_list.append((nscs, 0))
                nscs_label_list.append((nscs, 0))

        nscs_label_list_list.append(nscs_label_list)

    d = time.time()-t
    ret_info_dict['core_time'], t = d, time.time()

    # post processing
    # if EME overlap with IME, should be removed.
    # and a post processing on merging EME
    eme_list = eme_merger(lines, me_chars, ime_bbox_list)

    if eme_export_path:  # export the data
        page_info = {}
        page_info['pid'] = pid
        page_info['ilist'] = []
        page_info['elist'] = eme_list
        export_xml(page_info, eme_export_path, pdf_path, pid)

    d = time.time()-t
    ret_info_dict['io_time'] = d
    return ret_info_dict


def extract_eme(pdf_path):
    """

    :param pdf_path:
    :param xml_path:
    :return:
    """
    pn = get_page_num(pdf_path)
    prev_page_info = {}
    for pid in range(pn):
        eme_export_path = get_eme_path(pdf_path, pid)
        if not os.path.isfile(eme_export_path):
            prev_page_info = EME_font_stat_pipeline(
                pdf_path, pid,
                eme_export_path=eme_export_path,
                prev_page_info=prev_page_info)


#######################
#    ME Extraction    #
#######################
def extraction_done(pdf_path):
    pn = get_page_num(pdf_path)
    xml_path = get_xml_path(pdf_path)
    for pid in range(pn):
        eme_path = "{}.eme.{}.xml".format(xml_path, pid)
        ime_path = "{}.ime.{}.xml".format(xml_path, pid)
        if not os.path.isfile(eme_path):
            print("EME {} not exist".format(eme_path))
            return False
        if not os.path.isfile(ime_path):
            print("IME {} not exist".format(ime_path))
            return False
    return True


def extract_me(pdf_path):

    pdf_name = get_file_name_prefix(pdf_path)

    # TODO, place it outside

    duration_recorder.begin_timer("Begin ME Extraction")
    # load the setting here.
    tmp_pdf_path = get_tmp_path(pdf_path)

    if not os.path.isfile(tmp_pdf_path):
        shutil.copy(pdf_path, tmp_pdf_path)


    if extraction_done(pdf_path):
        print "ME extraction done for {}".format(pdf_path)
        return

    #if ext_settings.debug:
    #    convert2image(pdf_path)

    # batch extraction of lines
    pn = get_page_num(pdf_path)

    if ext_settings.debug:
        # the font is not useful in later stage
        #get_font_from_pdf(pdf_path, 0)  # just do it once, other wise, the parallel error?
        pass

    duration_recorder.begin_timer("Column-Line-Word")
    # This part should not be parallelized, only execute once

    export_exact_position(pdf_path)
    if ext_settings.ME_ANALYSIS_PARALLEL:
        print "parallized CLW threading"
        from pdfxml.pdf_util.clw_pipeline import clw_pdf_lines

        #Parallel(n_jobs=PARALLEL_SIZE)(
        #    delayed(clw_pdf_lines)(pdf_path, pid) for pid in range(pn))
        from multiprocessing import Process
        process_list = []
        for pid in range(pn):
            p = Process(target=clw_pdf_lines, args=(pdf_path, pid))
            p.start()
            process_list.append(p)

        for p in process_list:
            p.join()
    else:
        print "serialized CLW"
        if ext_settings.CLW_VERSION == CLW_OLD:
            from pdfxml.pdf_util.ppc_line_reunion import ppc_line_reunion
            for pid in range(pn):
                ppc_line_reunion(pdf_path, pid)
        elif ext_settings.CLW_VERSION == CLW_FEB:
            from pdfxml.pdf_util.clw_pipeline import clw_pdf_lines
            for pid in range(pn):
                clw_pdf_lines(pdf_path, pid)
        else:
            raise Exception("unknown version")

    duration_recorder.begin_timer("IME Extraction")
    extract_ime(pdf_path)
    duration_recorder.begin_timer("EME Extraction")
    extract_eme(pdf_path)
    duration_recorder.begin_timer("ME extraction finished")
