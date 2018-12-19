"""
The fraction path will be used to merge lines.

* a horizontal line: the vertical size is less than 1/3 of the median char size
* exist char vertical overlapping
* no chars crossing the path
* the nearest char should not be larger than 1/2 of the median char height


* after the path are identified, only merge the nearest lines that is within the range of the fraction line

# others
* vertical overlapped with some text lines, in the same columns
"""
from intervaltree import IntervalTree
from pdfxml.pdf_util.bbox import BBox
from pdfxml.pdf_util.pdf_extract import process_pdf_path
from pdfxml.pdf_util.pdfbox_wrapper import pdf_extract_chars
from pdfxml.pdf_util.char_process import get_median_char_height_by_char_list


def is_horizontal_line(path, m_char_height):
    """

    :param path:
    :param char_height:
    :return:
    """
    path_bbox = BBox(path.bbox)
    is_thin = path_bbox.height() < m_char_height / 3.0
    is_flat = path_bbox.width() > path_bbox.height()
    return is_thin and is_flat


def exist_overlapping_chars(path, char_list):
    """
    NOTE: a stricter version nees the chars to be in the same column

    :param path:
    :param char_list:
    :return:
    """
    pass


def get_fraction_line(pdf_path, pid):
    """
    get all pathes that is very likely to be fraction line

    :param pdf_path:
    :param pid:
    :return:
    """
    char_list = pdf_extract_chars(pdf_path, pid)
    median_char_height = get_median_char_height_by_char_list(char_list)

    vertical_it = IntervalTree()
    for char in char_list:
        if char.bbox[1] == char.bbox[3]:
            #print 'empty char', char
            continue
        #vertical_it.addi(char.bbox[1], char.bbox[3], char)
        vertical_it.addi(char.bbox[1], char.bbox[3], str(char.bbox))

    path_list = process_pdf_path(pdf_path, pid)
    filtered_path_list = []
    for path in path_list:
        #print "###"
        #print path
        if not is_horizontal_line(path, median_char_height):
            #print 'not horizontal'
            continue

        # TODO, this checking should be after the column detection
        # but it's alright now for the AggieSTEM case
        print "WARNING: "
        print "TODO, this checking should be after the column detection"
        print "but it's alright now for the AggieSTEM case"

        overlapped_char_list = vertical_it[path.bbox[1]:path.bbox[3]+0.00001]
        if len(overlapped_char_list) == 0:
            #print 'no overlapping chars'
            continue
        filtered_path_list.append(path)

    return filtered_path_list


if __name__ == "__main__":
    pass