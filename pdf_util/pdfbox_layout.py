"""

"""

import numpy as np
from pdfxml.pdf_util.char_process import char_list2str
from pdfxml.pdf_util.layout_util import get_char_list_bbox


def is_double_column(pdf_path, pid, debug=False):
    """
        The idea is that if there are two cluster of begin position , then double column

    :param pdf_path:
    :param pid:
    :return:
    """
    from pdfxml.pdf_util.pdfbox_line_merging import pdf_extract_lines_raw
    from pdfxml.pdf_util.pdfbox_wrapper import get_pdf_page_size

    char_list_list = pdf_extract_lines_raw(pdf_path, pid)

    page_size = get_pdf_page_size(pdf_path, pid)
    page_width = page_size['width']

    # get the boundary of the column, collect the startpoint, and end point, use 0.95 quantile
    start_pos_list = []
    end_pos_list = []
    quantile = 0.90
    for char_list in char_list_list:
        # remove line with less than 10 chars
        if len(char_list) < 30:
            continue
        bbox = get_char_list_bbox(char_list)
        start_pos_list.append(bbox.left())
        end_pos_list.append(bbox.right())

    if len(start_pos_list) == 0 or len(end_pos_list) == 0:
        # it's an empty page.
        #raise Exception("could not get the left/right boundary")
        return False

    start_pos = np.percentile(start_pos_list, int((1-quantile)*100))
    end_pos = np.percentile(end_pos_list, int(quantile*100))
    if debug:
        #plt.hist(start_pos_list)
        print("The main column boundary {} {}".format(start_pos, end_pos))

    if end_pos < page_width / 2 or start_pos > page_width/2:
        # if only half of the column have enough lines.
        return True

    center_pos = (start_pos+end_pos)/2
    good_line_count = 0
    total_count = 0.0

    for char_list in char_list_list:
        # remove line with less than 10 chars
        if len(char_list) < 30:
            continue

        bbox = get_char_list_bbox(char_list)
        if bbox.left() < bbox.right() < center_pos or \
                bbox.right() > bbox.left() > center_pos:
            good_line_count += 1
            if debug:
                tmp_str = char_list2str(char_list)
                print "Good Line", tmp_str, bbox
        total_count += 1
        #print "BadLine", total_count

    if debug:
        line_str_list = []
        for char_list in char_list_list:
            line_str_list.append(char_list2str(char_list))

    threshold = 0.6
    if float(good_line_count) / total_count > threshold:
        return True
    else:
        return False


