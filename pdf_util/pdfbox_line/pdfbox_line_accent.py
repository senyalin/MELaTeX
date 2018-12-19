"""
Merge the accent with the corresponding lines
"""
from pdfxml.pdf_util.layout_util import get_char_list_bbox
from pdfminer.layout import LTChar
from pdfxml.pdf_util.word_seg_process import re_group_char_list_seg


def only_accent(char_list):
    """
    only accent symbols exist in the line

    :param char_list:
    :return:
    """
    # check for accent
    is_only_accent = True
    from pdfxml.me_taxonomy.math_resources import accent_name_list
    for c in char_list:
        if isinstance(c, LTChar) and c.get_text() not in accent_name_list:
            is_only_accent = False
    return is_only_accent


def merge_accent(char_list_list, fontname2space):
    """
    merge the accent

    :param char_list_list:
    :return:
    """
    line_bbox_list = []
    for char_list in char_list_list:
        line_bbox = get_char_list_bbox(char_list)  # not removing the accent
        line_bbox_list.append(line_bbox)
        #print char_list2str(char_list)  # for debugging only

    cur_line_idx_list = range(len(char_list_list))
    cur_line_idx_list.sort(key=lambda lid: -line_bbox_list[lid].top())

    # for each accent line, merge with the first line under it. and h overlap with it
    used_line_id_list = []

    # the line might be occur before the accent
    accent_idx2target_idx = {}
    for i, line_idx in enumerate(cur_line_idx_list):
        if line_idx in used_line_id_list:
            continue

        if only_accent(char_list_list[cur_line_idx_list[i]]):
            cur_bbox = line_bbox_list[line_idx]
            found_next_line = False
            for j in range(0, len(cur_line_idx_list)):
                # check all lines
                cand_bbox = line_bbox_list[cur_line_idx_list[j]]
                #if cur_bbox.h_overlap(cand_bbox) and cand_bbox.top() < cur_bbox.bottom():
                if cur_bbox.h_overlap(cand_bbox):
                    cond1 = cand_bbox.top() < cur_bbox.top()
                    # but not self
                    cond2 = cand_bbox.bottom() <= cur_bbox.bottom() <= \
                            cur_bbox.top() <= cand_bbox.top() and i != j

                    if cond1 or cond2:
                        accent_idx2target_idx[line_idx] = cur_line_idx_list[j]

                        used_line_id_list.append(line_idx)
                        used_line_id_list.append(cur_line_idx_list[j])

                        #tmp_char_list = char_list_list[line_idx]
                        #tmp_char_list.extend(char_list_list[cur_line_idx_list[j]])
                        #return_char_list_list.append(tmp_char_list)
                        found_next_line = True
                        break
            if not found_next_line:
                pass
        else:
            #return_char_list_list.append(char_list_list[line_idx])
            pass

    return_char_list_list = []
    used_line_id_list = []
    target_idx2accent_idx = {v:k for k, v in accent_idx2target_idx.items()}
    for i, line_idx in enumerate(cur_line_idx_list):
        if line_idx in used_line_id_list:
            continue

        if line_idx in accent_idx2target_idx:
            tmp_char_list = []
            tmp_char_list.extend(char_list_list[line_idx])
            tmp_char_list.extend(char_list_list[accent_idx2target_idx[line_idx]])
            return_char_list_list.append(tmp_char_list)
            used_line_id_list.append(line_idx)
            used_line_id_list.append(accent_idx2target_idx[line_idx])
        elif line_idx in target_idx2accent_idx:
            tmp_char_list = []
            tmp_char_list.extend(char_list_list[line_idx])
            tmp_char_list.extend(char_list_list[target_idx2accent_idx[line_idx]])
            return_char_list_list.append(tmp_char_list)
            used_line_id_list.append(line_idx)
            used_line_id_list.append(target_idx2accent_idx[line_idx])
        else:
            return_char_list_list.append(char_list_list[line_idx])

    for char_list in return_char_list_list:
        #print char_list2str(char_list)
        pass

    # sort the return _char_list_list based on the top
    line_bbox_list = []
    for char_list in return_char_list_list:
        line_bbox = get_char_list_bbox(char_list)  # not removing the accent
        line_bbox_list.append(line_bbox)
    cur_line_idx_list = range(len(return_char_list_list))
    cur_line_idx_list.sort(key=lambda lid: -line_bbox_list[lid].top())

    # re-order
    new_return_char_list_list = []
    for line_idx in cur_line_idx_list:
        new_return_char_list_list.append(return_char_list_list[line_idx])
    return_char_list_list = new_return_char_list_list

    res_char_list_list = []
    for char_list in return_char_list_list:
        res_char_list_list.append(re_group_char_list_seg(char_list, fontname2space))
    return res_char_list_list