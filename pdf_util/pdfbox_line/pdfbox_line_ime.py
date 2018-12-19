from pdfxml.pdf_util.char_process import get_latex_val_of_lt_char
from pdfxml.pdf_util.layout_util import get_char_list_bbox, get_width
from pdfminer.layout import LTChar


def merge_line_ime(char_list_list):
    """
    Though it's called IME processing,
    however it's only merging the bind var,
    no matter it's IME or EME.

    a better name might be merge big op

    only merge based on the bind var operator

    :param char_list_list:
    :return:
    """
    line_bbox_list = []
    for char_list in char_list_list:
        line_bbox = get_char_list_bbox(char_list)  # not removing the accent
        line_bbox_list.append(line_bbox)
    cur_line_idx_list = range(len(char_list_list))
    cur_line_idx_list.sort(key=lambda lid: -line_bbox_list[lid].top())

    uppper_under_line_idx = list()
    line_idx2line_idx_list = {}

    res_char_list_list = []
    for i, line_idx in enumerate(cur_line_idx_list):
        left_bound, right_bound = 1000000, -1
        for char in char_list_list[line_idx]:
            if not isinstance(char, LTChar):
                continue
            latex_val = get_latex_val_of_lt_char(char)
            #print latex_val
            if latex_val in ['\\sum', '\\prod']:
                left_bound = min(left_bound, char.bbox[0]-get_width(char.bbox))
                right_bound = max(right_bound, char.bbox[2]+get_width(char.bbox))
        if left_bound > right_bound:
            line_idx2line_idx_list[line_idx] = [line_idx]
            continue

        line_idx2line_idx_list[line_idx] = [line_idx]
        if i != 0:
            prev_line_idx = cur_line_idx_list[i-1]
            prev_bbox = line_bbox_list[prev_line_idx]
            if prev_bbox.left() > left_bound and prev_bbox.right() < right_bound:
                line_idx2line_idx_list[line_idx].append(prev_line_idx)
                uppper_under_line_idx.append(prev_line_idx)

        if i != len(cur_line_idx_list)-1:
            next_line_idx = cur_line_idx_list[i+1]
            next_bbox = line_bbox_list[next_line_idx]
            if next_bbox.left() > left_bound and next_bbox.right() < right_bound:
                line_idx2line_idx_list[line_idx].append(next_line_idx)
                uppper_under_line_idx.append(next_line_idx)

    res_char_list_list = []
    for line_idx in cur_line_idx_list:
        if line_idx in uppper_under_line_idx:
            continue
        tmp_char_list = []
        for tmp_li in line_idx2line_idx_list[line_idx]:
            tmp_char_list.extend(char_list_list[tmp_li])
        res_char_list_list.append(tmp_char_list)

    return res_char_list_list