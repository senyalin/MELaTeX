from pdfxml.InftyCDB.data_portal.data_portal_split_chars import load_chars_by_me_idx
from pdfxml.me_layout.layout_configuration.script_config import ScriptConfig
from pdfxml.me_layout.test_infty_cdb_pipeline import get_cpr_from_me_elems


def load_sc_for_infty(me_idx):
    elem_list = load_chars_by_me_idx(me_idx)
    gd_cpr_list = get_cpr_from_me_elems(elem_list)

    sc = ScriptConfig()
    for gd_cpr in gd_cpr_list:
        sc.add_triple(gd_cpr[0], gd_cpr[1], gd_cpr[2])
    for elem in elem_list:
        if elem['relation'] == 'TOP':
            sc.add_triple(elem['cid'], -1, None)  # None is the convention.
    return sc