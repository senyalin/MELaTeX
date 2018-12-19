import os
import copy
from pdfxml.file_util import load_serialization, dump_serialization
from pdfxml.InftyCDB.macros import glyph_type_map
from pdfxml.InftyCDB.data_portal.data_portal import load_me_elems_xlsx
from pdfxml.InftyCDB.data_portal.data_portal_split_chars import load_chars_by_me_idx
from pdfxml.path_util import SHARED_FOLDER, infty_cdb_folder, infty_cdb_tmp_folder


def get_glyph_type(name):
    """
    The current logic short cut: * and *_greek are all mapped to '*' type

    :param name: given the name in the inftyCDB
    :return:
    """
    name = copy.copy(name)
    if name.startswith("\\"):
        name = name[1:]

    for glyph_type, name_list in glyph_type_map.items():
        if name in name_list:
            return glyph_type[:glyph_type.index('_')]
    print "{} with glyph type unkonwn".format(name)
    return 'unknown'


def left_relation_exist(me_idx):
    elem_list = load_chars_by_me_idx(me_idx)
    for elem in elem_list:
        if elem['relation'] in ['LSUP', 'LSUB']:
            return True
    return False


def get_all_me_idx_list():
    """
    This will be the list of me_idx to run experiment with
    :return:
    """
    cache_path = "{}/all_me_idx_list.pkl".format(infty_cdb_tmp_folder)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)
    xlsx_path = "{}/InftyCDB-1/resources/me.xlsx".format(SHARED_FOLDER)
    elem_list = load_me_elems_xlsx(xlsx_path)
    me_idx_set = set()
    for elem in elem_list:
        me_idx_set.add(elem['me_idx'])
    me_idx_list = list(me_idx_set)
    dump_serialization(me_idx_list, cache_path)
    return me_idx_list
