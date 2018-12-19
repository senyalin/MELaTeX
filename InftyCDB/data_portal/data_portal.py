"""
Export Math related symbols here
"""
import os
import copy
import xlrd
from pdfxml.file_util import load_general, dump_general
from pdfxml.file_util import load_serialization, dump_serialization, test_folder_exist_for_file_path
from pdfxml.path_util import PROJECT_FOLDER, SHARED_FOLDER, infty_cdb_folder, infty_cdb_tmp_folder, infty_cdb_folder
from pdfxml.InftyCDB.data_portal.data_portal_img import fname2shape
# the im2shape is a pre-build cache of the image size
# It's useful because the InftyCDB's coordinate is up side down w.r.t. the PDF system
# im2shape = fname2shape()
im2shape = None


#########
# utility function
#########
def get_cid2char(elem_list):
    """
    from cid to the detail char information

    :param elem_list:
    :return:
    """
    cid2char = {}
    for elem in elem_list:
        cid2char[elem["cid"]] = elem
    return cid2char


def get_cid2pid(elem_list):
    """
    children id to parent id

    :param elem_list:
    :return:
    """
    cid2pid = {}
    for elem in elem_list:
        cid2pid[elem["cid"]] = elem["pid"]
    return cid2pid


def get_pid2cidset(elem_list):
    """
    from parent to set of children id

    :param elem_list:
    :return:
    """
    pid2cidset = {}
    cid2pid = get_cid2pid(elem_list)
    for cid, pid in cid2pid.items():
        if pid not in pid2cidset:
            pid2cidset[pid] = set()
        pid2cidset[pid].add(cid)
    return pid2cidset


def get_me_idx_list():
    """
    get all the me_idx, no matter runnable or not

    :return: list[int]
    """
    cache_path = "{}/tmp/me_idx_list.pkl".format(infty_cdb_folder)
    test_folder_exist_for_file_path(cache_path)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    me_xlsx_path = "{}/InftyCDB-1/resources/me.xlsx".format(SHARED_FOLDER)
    wb = xlrd.open_workbook(me_xlsx_path)
    sheet_names = wb.sheet_names()

    me_idx_list = []
    ws = wb.sheet_by_index(0)
    for r_idx in range(ws.nrows):
        row = ws.row(r_idx)
        me_idx = int(row[20].value)
        me_idx_list.append(me_idx)

    me_idx_list = list(set(me_idx_list))
    dump_serialization(me_idx_list, cache_path)
    return me_idx_list


def get_cid2me_idx():
    """
    char id to me idx
    :return:
    """
    cache = "{}/cid2me_idx.pkl".format(infty_cdb_tmp_folder)
    test_folder_exist_for_file_path(cache)
    if os.path.isfile(cache):
        return load_serialization(cache)
    cid2me_idx = {}
    me_xlsx_path = "{}/InftyCDB-1/resources/me.xlsx".format(SHARED_FOLDER)
    elem_list = load_me_elems_xlsx(me_xlsx_path)
    for elem in elem_list:
        cid2me_idx[elem['cid']] = elem['me_idx']
    dump_serialization(cid2me_idx, cache)
    return cid2me_idx


#############
# load char information from xlsx file
#############
def load_me_elems_xlsx(infty_cdb_xlsx_path):
    """

    :param infty_cdb_xlsx_path:
    :return:
    """
    global im2shape
    if im2shape is None:
        im2shape = fname2shape()

    wb = xlrd.open_workbook(infty_cdb_xlsx_path)
    sheet_names = wb.sheet_names()

    me_elems = []
    ws = wb.sheet_by_index(0)
    for r_idx in range(ws.nrows):
        row = ws.row(r_idx)
        # print len(row)
        cid = int(row[0].value)
        font = row[3].value # filter out Accent from horizontal
        code, name, pid, rel = row[4].value, row[5].value, int(row[13].value), row[14].value

        code = str(code)
        if code.endswith(".0"):
            code = code[:-2]

        fname = row[15].value
        me_idx = int(row[20].value)
        #print fname
        h, w = im2shape[fname]

        bbox = [float(w.value) for w in row[16:20]]

        new_bbox = copy.copy(bbox)
        new_b = h - bbox[3]
        new_t = h - bbox[1]
        new_bbox[1] = new_b
        new_bbox[3] = new_t

        me_elems.append({
            'cid': cid,
            'code': code,
            'name': name,
            'pid': pid,
            'relation': rel,
            'raw_bbox': bbox,  # upside down
            'bbox': new_bbox,
            'fname': fname,
            'me_idx': me_idx,
            'shape': im2shape[fname]
        })

    return me_elems


def load_char_map(refresh=False):
    """
    load mathematical chars from the CSV file
    NOTE: Dec. 10, later use the XLSX file with less noise.

    :param refresh:
    :return: the dict from the char id to char info
    """
    #cached_path = "{}/InftyCDB/cache_data/chars.json".format(PROJECT_FOLDER)
    cached_path = "{}/tmp/chars.json".format(infty_cdb_folder)
    test_folder_exist_for_file_path(cached_path)
    if os.path.isfile(cached_path) and not refresh:
        return load_general(cached_path)

    print('rebuild cache from the xlsx file')
    me_xlsx_path = "{}/InftyCDB-1/resources/me.xlsx".format(SHARED_FOLDER)
    me_elems = load_me_elems_xlsx(me_xlsx_path)
    cid2info = {}
    for me_elem in me_elems:
        cid2info[me_elem['cid']] = me_elem

    dump_general(cid2info, cached_path)
    return cid2info


#############
# split the chars at the level of ME
#############
def get_pid2cid_list():
    """

    :return: map from parent char id to list of children
    """
    cache_path = 'pid2cid_list.pkl'
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    cid2info = load_char_map()
    pid2cid_list = {}
    for cid, info in cid2info.items():
        if info['pid'] == -1:
            continue
        if not pid2cid_list.has_key(info['pid']):
            pid2cid_list[info['pid']] = []
        pid2cid_list[info['pid']].append(cid)

    dump_serialization(pid2cid_list, cache_path)

    return pid2cid_list


def get_name2code_set():
    """
    name is the glyph name,
    code is the unique id for the pair of glyph name & font

    one glyph name could have multiple code in different fonts.

    :return:
    """
    from pdfxml.path_util import SHARED_FOLDER
    #name2code_cache_path = "{}/tmp/name2code.pkl".format(infty_cdb_folder)
    name2code_cache_path = "{}/InftyCDB-1/cache_data/name2code.json".format(SHARED_FOLDER)
    if os.path.isfile(name2code_cache_path):
        name2code_list = load_general(name2code_cache_path)
        name2code_set = {}
        for name, code_list in name2code_list.items():
            name2code_set[name] = set(code_list)
        return name2code_set

    cid2info = load_char_map()
    name2code_set = {}
    for c in cid2info.values():
        if c['name'] not in name2code_set:
            name2code_set[c['name']] = set()
        name2code_set[c['name']].add(c['code'])

    name2code_list = {}
    for name, code_set in name2code_set.items():
        name2code_list[name] = list(code_set)
    dump_general(name2code_list, name2code_cache_path)

    return name2code_set


def get_code2name():
    """
    based on name2code_set to build map from code 2 name
    :return:
    """
    name2code_set = get_name2code_set()
    code2name = {}
    for name, code_set in name2code_set.items():
        for code in code_set:
            code2name[code] = name
    return code2name


##################
# batch processing
##################

# NOTE : the coordinate is with the left-top as the original point

def filter_me():
    """
    InftyCDB-1.csv is the raw data file,
    This script will print the line related to ME to the screen
        and pipe them to another file

    :return:
    """
    full_infty_cdb_path = "{}/InftyCDB-1.csv".format(infty_cdb_folder)
    lines = open(full_infty_cdb_path).readlines()
    for line in lines:
        ws = line.split(",")
        if ws[6][1:-1] == "math":
            print(line.strip())


if __name__ == "__main__":
    #infty_cdb_xlsx_path = infty_cdb_folder+"/tmp/me.xlsx"
    #load_me_elems_xlsx()
    #load_char_map()
    get_name2code_set()
