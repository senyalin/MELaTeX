"""
merge lines by fraction

1. get the fraction
2. merge the two nearest lines no larger than 1/2 of the char height distance.
"""

from pdfxml.search.bs import find_lt, find_gt, find_gt_idx, find_lt_idx

from pdfxml.pdf_util.word_seg_process import char_list_list2char_list, char_list2char_list_list
from pdfxml.pdf_util.char_process import get_median_char_height_by_char_list, char_list2bbox, char_list2str


def merge_line_fraction(char_list_list, fraction_path_list):
    char_list = char_list_list2char_list(char_list_list)
    median_char_height = get_median_char_height_by_char_list(char_list)

    # char_list_list, sort by the vertical center position
    line_v_c_list = []  # vertical center
    org_line_bbox_list = []
    for char_list in char_list_list:
        bbox = char_list2bbox(char_list)
        line_v_c_list.append(bbox.v_center())
        org_line_bbox_list.append(bbox)
    line_idx_list = range(len(char_list_list))
    line_idx_list.sort(key=lambda line_idx: -line_v_c_list[line_idx])

    sorted_char_list_list = []
    sorted_line_bbox_list = []
    for line_idx in line_idx_list:
        sorted_char_list_list.append(char_list_list[line_idx])
        sorted_line_bbox_list.append(org_line_bbox_list[line_idx])
    sorted_v_c_list = [-bbox.v_center() for bbox in sorted_line_bbox_list]

    from pdfxml.pdf_util.unionfind import UnionFind
    uf = UnionFind()
    for idx in range(len(sorted_v_c_list)):
        uf.add_node(idx)

    for path in fraction_path_list:
        # get the nearest lines
        # find_lt()
        # another issue to concern is the order of the char_list_list?
        # change to nscs_list, merge the nscs_list, and then convert the char_list for the line
        gt_idx = find_gt_idx(sorted_v_c_list, -path.bbox[1])
        lt_idx = find_lt_idx(sorted_v_c_list, -path.bbox[3])
        if gt_idx is None or lt_idx is None:
            continue
        if gt_idx <= lt_idx:
            raise Exception("TODO")
        assert gt_idx > lt_idx
        if abs(sorted_v_c_list[gt_idx] - sorted_v_c_list[lt_idx]) < 3 * median_char_height:  # merge the two lines
            uf.merge(lt_idx, gt_idx)
        else:
            print abs(sorted_v_c_list[gt_idx] - sorted_v_c_list[lt_idx])
            prev_line_str = char_list2str(sorted_char_list_list[lt_idx])
            next_line_str = char_list2str(sorted_char_list_list[gt_idx])
            print prev_line_str
            print next_line_str
            print 'failed to merge lines?'
    idx_group_list = uf.get_groups()

    # merged line list
    merged_line_list = []
    for idx_group in idx_group_list:
        nscs_list = []
        for line_idx in idx_group:
            tmp_nscs_list = char_list2char_list_list(sorted_char_list_list[line_idx])
            nscs_list.extend(tmp_nscs_list)
        merged_line_list.append(char_list_list2char_list(nscs_list))

    # sort the line again
    merged_line_bbox_list = [char_list2bbox(line) for line in merged_line_list]
    merged_line_idx_list = range(len(merged_line_list))
    merged_line_idx_list.sort(key=lambda merge_line_idx: -merged_line_bbox_list[merge_line_idx].top()) # minus because start from the bottom

    sorted_merged_line_list = [merged_line_list[line_idx] for line_idx in merged_line_idx_list]
    return sorted_merged_line_list
