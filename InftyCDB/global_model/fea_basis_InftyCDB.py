"""
For the InftyCDB dataset,
construct the l1 feature for the height ratio and nycd
The feature is calculated at the character level, not group level

One special case: the reversed relation

There are two major parts of the functions:
 * data preparation
 * feature calculation
"""
import os
from pdfxml.path_util import PROJECT_FOLDER, infty_cdb_folder
from pdfxml.file_util import load_serialization, dump_serialization
from pdfxml.InftyCDB.data_portal.data_portal_split_chars import get_cached_chars_path_by_me_idx
from pdfxml.InftyCDB.data_portal.data_portal import load_me_elems_xlsx
from pdfxml.InftyCDB.infty_cdb_util import get_glyph_type
from pdfxml.InftyCDB.normalize_height.char_adjust_bbox import adjust_bbox_h_gt_name
from pdfxml.me_layout.layout_prediction.pos_features import fea_name2fea_func


######
# prepare data, including
# * prepare_data_one
# * batch_prepare_data
# * test_prepare_data
######
def prepare_parent_child_relation_list_one_me(me_idx):
    """
    1. prepare data for different relation
    2. Only keep the relation for the symbol with known x-y-z configration
    3. [NOTE, not done?] normalize the bbox for chars

    :param me_idx: me_idx as the identifier
    :return: list of dict[parent, children, relation]
    :rtype: list[dict]
    """

    chars_path = get_cached_chars_path_by_me_idx(me_idx)
    chars = load_serialization(chars_path)

    cid2cinfo = {}
    for c in chars:
        cid2cinfo[c['cid']] = c

    pair_list = []
    for c in chars:
        if c['pid'] == -1:
            continue
        if not cid2cinfo.has_key(c['pid']):
            print 'no info for pid', c
            continue

        cname = c['name']
        pname = cid2cinfo[c['pid']]['name']
        #print cname, pname
        c_adj_type = get_glyph_type(cname)
        p_adj_type = get_glyph_type(pname)
        adj_type_list = ['y', 'xy', 'yz', 'xyz', 'hxy', 'hxyz']
        if c_adj_type not in adj_type_list:
            continue
        if p_adj_type not in adj_type_list:
            continue
        print cname, c_adj_type, pname, p_adj_type, c['relation']

        pair_list.append({
            'pinfo': cid2cinfo[c['pid']],
            'cinfo': c,
            'relation': c['relation']
            })
    return pair_list


def prepare_parent_child_relation_list_batch():
    """
    merge all the triples

    :return: :return: list of dict[parent, children, relation]
    """
    cache_path = "{}/tmp/hor_sub_sup_alphanumeric.pkl".format(infty_cdb_folder)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    res_list = []
    # get all me_idx here
    chars_folder = "{}/crop_chars".format(infty_cdb_folder)
    for fname in os.listdir(chars_folder):
        me_idx = int(fname[fname.rindex("_")+1:-4])
        pair_list = prepare_parent_child_relation_list_one_me(me_idx)
        res_list.extend(pair_list)
        print me_idx, len(pair_list)

    dump_serialization(res_list, cache_path)
    return res_list


######
# feature
######
def get_fea_val_by_fea_name(fea_name):
    """

    :param fea_name:
    :type fea_name: basestring
    :return: dict from relative position type to list of feature values
    :rtype: dict[string_wx, list[float]]
    """

    assert(fea_name in fea_name2fea_func)
    fea_func = fea_name2fea_func[fea_name]

    cache_path = "{}/fea_val/{}.pkl".format(infty_cdb_folder, fea_name)
    if os.path.isfile(cache_path):
        return load_serialization(cache_path)

    rel_list = prepare_parent_child_relation_list_batch()
    rel2fea_val_list = {
        "HORIZONTAL": [], "RSUP": [], "RSUB": [], "REV_RSUB": [], "REV_RSUP": []
    }

    for pr in rel_list:
        if not pr['relation'] in ["HORIZONTAL", "RSUP", "RSUB"]:
            continue

        # adjust bbox here
        p_bbox = adjust_bbox_h_gt_name(
            pr['pinfo']['bbox'],
            pr['pinfo']['name'])

        c_bbox = adjust_bbox_h_gt_name(
            pr['cinfo']['bbox'],
            pr['cinfo']['name'])

        fea_val = fea_func(p_bbox, c_bbox)
        rel2fea_val_list[pr['relation']].append(fea_val)

        if pr['relation'] in ["RSUP", "RSUB"]:
            # calculate the feature value here
            rev_fea_val = fea_func(c_bbox, p_bbox)
            rel2fea_val_list["REV_"+pr['relation']].append(rev_fea_val)

    dump_serialization(rel2fea_val_list, cache_path)
    return rel2fea_val_list

def get_rel_str2fea_val_list_nycd():
    """
    dump out the normalized y center difference
    """
    return get_fea_val_by_fea_name("normalized_ycenter_diff_AB")


def get_rel_str2fea_val_list_hr():
    """
    dump the height ratio feature
    """
    return get_fea_val_by_fea_name("height_ratio_AB")


def test_prepare_data():
    """
    TODO, some file in crop_me don't have corresponding crop_chars?
    or path problem
    """
    me_idx = 28000474  # $(z,\sqrt{-\rho(z)})$,
    me_idx = 28000767
    pcr_list = prepare_parent_child_relation_list_one_me(me_idx)
    for pcr in pcr_list:
        for k, v in pcr.items():
            print k, v
        print ""



##########
# relation
##########
def rel_stat():
    """
    statistic of count of different relation

    :return:
    """

    rel_list = load_me_elems_xlsx("{}/InftyCDB-1/resources/me.xlsx".format(SHARED_FOLDER))
    #rel_list = batch_prepare_data()
    # get the count and draw stat for each
    rel2c = {
        "HORIZONTAL": 0,
        "RSUP": 0,
        "RSUB": 0
        }
    for pr in rel_list:
        if not rel2c.has_key(pr['relation']):
            continue

        rel2c[pr['relation']] += 1
    print rel2c


############
# visual modules
############
def draw_hist_hr():
    rel2hr_list = get_rel_str2fea_val_list_hr()
    for rel, hr_list in rel2hr_list.items():
        plt.clf()
        plt.hist(hr_list, 30)
        fig_path = "{}/hist_fig/hr_hist_{}.png".format(infty_cdb_folder, rel)
        plt.savefig(fig_path)


def draw_hist_nycd():
    rel2v_list = get_rel_str2fea_val_list_nycd()
    for rel, vlist in rel2v_list.items():
        plt.clf()
        plt.hist(vlist, 30)
        fig_path = "{}/hist_fig/nycd_hist_{}.png".format(infty_cdb_folder, rel)
        plt.savefig(fig_path)

if __name__ == '__main__':
    pass
    #test_prepare_data()
    #prepare_parent_child_relation_list_batch()
    #get_rel_str2fea_val_list_nycd()
    #rel_stat()
    #draw_hist_hr()
    ##draw_hist_nycd()