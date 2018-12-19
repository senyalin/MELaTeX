def get_all_substrings(input_string):
    """
    get all sub strings
    :param input_string:
    :return:
    """
    length = len(input_string)
    return [input_string[i:j+1] for i in xrange(length) for j in xrange(i,length)]


def find_element_in_list(element, list_element, start_i=0):
    try:
        index_element = list_element.index(element, start_i)
        return index_element
    except ValueError:
        return -1


def default_equal(e1, e2):
    return e1 == e2


def is_subsequence(seq1, seq2, equal_func=default_equal):
    """
    check whether seq1 is a sub sequence of seq2

    :param seq1:
    :param seq2:
    :return:
    """
    assert isinstance(seq1, list) and isinstance(seq2, list)
    assert len(seq1) > 0

    start_pos_list = []
    for i, elem2 in enumerate(seq2):
        #if elem2 == seq1[0]:
        if equal_func(elem2, seq1[0]):
            start_pos_list.append(i)

    for start_i in start_pos_list:
        found_in_consistent = False
        j = 0
        while j < len(seq1):
            if start_i+j >= len(seq2):
                break
            if not equal_func(seq1[j], seq2[start_i + j]):
                found_in_consistent = True
                break
            j += 1

        # if no the j==len(seq1) checking, many bad are added.
        if j == len(seq1) and not found_in_consistent:
            return True

    return False


def subsequence_pos(seq1, seq2, equal_func=default_equal):
    """
    check whether seq1 is a sub sequence of seq2

    :param seq1:
    :param seq2:
    :return:
    """
    assert isinstance(seq1, list) and isinstance(seq2, list)
    assert len(seq1) > 0

    start_pos_list = []
    for i, elem2 in enumerate(seq2):
        #if elem2 == seq1[0]:
        if equal_func(elem2, seq1[0]):
            start_pos_list.append(i)

    for start_i in start_pos_list:
        found_in_consistent = False
        j = 0
        while j < len(seq1):
            if start_i+j >= len(seq2):
                break
            if not equal_func(seq1[j], seq2[start_i + j]):
                found_in_consistent = True
                break
            j += 1

        # if no the j==len(seq1) checking, many bad are added.
        if j == len(seq1) and not found_in_consistent:
            return start_i

    return None


def is_non_consecutive_subsequence(s, t):
    """

    :param s:
    :param t:
    :return:
    """
    start = 0
    for i in range(len(s)):
        c = s[i]
        start = t.index(c) if c in t else -1
        if start == -1:
            return False
        start += 1
    return True



