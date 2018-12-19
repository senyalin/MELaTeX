from pdfminer.layout import LTChar


def is_empty_line(char_list):
    """

    :param char_list:
    :return:
    """
    for c in char_list:
        if isinstance(c, LTChar) and c.get_text() not in [' ', 'space']:
            return False
    return True


def remove_empty_lines(char_list_list):
    """
    empty means only have LTAnno in them
    :param char_list_list:
    :return:
    """
    new_char_list_list = []
    for char_list in char_list_list:
        if is_empty_line(char_list):
            continue
        new_char_list_list.append(char_list)
    return new_char_list_list
