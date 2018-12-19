import os

from pdfxml.me_extraction.ME_separation import EME_font_stat_pipeline, assess_ime
from pdfxml.me_extraction.MathEval import get_info
from pdfxml.path_util import get_eme_path, get_ime_path


def load_eme_bbox_list(pdf_path, pid):
    """

    :param pdf_path:
    :param pid:
    :return:
    """
    # load the EME
    pd_path = get_eme_path(pdf_path, pid)
    if not os.path.isfile(pd_path):
        # TODO, call the stage4 procedure to create the EME automatically
        EME_font_stat_pipeline(pdf_path, pid, eme_export_path=pd_path)

    flag, me_list = get_info(pd_path)
    if not flag:
        print "Try to load from ", pd_path
        raise Exception("no ME extracted for page ", pid)

    bbox_list = []
    for me in me_list:
        r = me['rect']
        bbox_list.append([r['l'], r['b'], r['r'], r['t']])
    return bbox_list


def load_ime_bbox_list(pdf_path, pid):
    """

    :param pdf_path:
    :param pid:
    :return:
    """
    ime_path = get_ime_path(pdf_path, pid)
    if not os.path.isfile(ime_path):
        assess_ime(pdf_path, pid, ime_path)

    # load the bbox here
    flag, formulas = get_info(ime_path)
    ime_bbox_list = []
    for f in formulas:
        if not f['type'] == 'I':
            continue
        r = f['rect']
        bbox = r['l'], r['b'], r['r'], r['t']
        ime_bbox_list.append(bbox)
    return ime_bbox_list

