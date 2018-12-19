from pdfxml.pdf_util.char_process import char_list2str, char_list2bbox
from pdfxml.intervaltree_2d import IntervalTree2D
from pdfxml.pdf_util.pdf_extract import get_page_num
from pdfxml.pdf_util.models.layout_line import is_heading_line_by_str, is_abstract_head, is_reference_head


def get_ignore_region(pdf_path):
    """
    :param pdf_path:
    :return:
        return pid2intervaltree
    """
    from pdfxml.me_extraction.me_font_stat_stage4 import internal_get_llines
    pn = get_page_num(pdf_path)

    pid2it2d = {}

    all_lines = []
    for pid in range(pn):
        lines = internal_get_llines(None, pdf_path, pid)
        for line in lines:
            line_str = char_list2str(line)
            is_heading = is_heading_line_by_str(line_str)
            all_lines.append({
                'char_list': line,
                'line_str': line_str,
                'pid': pid,
                'is_heading': is_heading
            })

    # first process the abstract part
    abstract_heading_line_idx = None
    for i, line_info in enumerate(all_lines):
        if line_info['is_heading'] and \
                is_abstract_head(line_info['line_str']):
            abstract_heading_line_idx = i
            break
        if line_info['pid'] > pn/2:
            # should not be at the second half of the document.
            break

    if abstract_heading_line_idx is not None:
        for i in range(abstract_heading_line_idx):
            pid = all_lines[i]['pid']
            if pid not in pid2it2d:
                pid2it2d[pid] = IntervalTree2D()
            pid2it2d[pid].add_bbox_only(char_list2bbox(all_lines[i]['char_list']))

    ignore_begin = False
    for line_info in all_lines:
        # ignore the abstraction and the reference
        if line_info['is_heading']:
            abs_head = is_abstract_head(line_info['line_str'])
            ref_head = is_reference_head(line_info['line_str'])
            if abs_head or ref_head:
                ignore_begin = True
            else:
                ignore_begin = False
        else:
            if ignore_begin:
                pid = line_info['pid']
                if pid not in pid2it2d:
                    pid2it2d[pid] = IntervalTree2D()
                pid2it2d[pid].add_bbox_only(
                    char_list2bbox(line_info['char_list']))
    return pid2it2d
