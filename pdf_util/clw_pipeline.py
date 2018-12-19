"""
column, line, word pipeline
should be based on the ppc line detection algorithm
"""
from pdfxml.pdf_util.pdf_extract_pdfbox import pdf_extract_lines


def clw_pdf_lines(pdf_path, pid):
    return pdf_extract_lines(pdf_path, pid)


if __name__ == "__main__":
    test_get_line = "10.1.1.1.2016_12"
    pass
