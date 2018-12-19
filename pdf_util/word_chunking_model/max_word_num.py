"""
find the seperation that maximize the words.
letters
puncts
others

Based on statistics from the NLTK package,
 the 0.95 quartile of the word length is 15,
 if a word with larger than this length exist,
 I need try to call the segmenter utility for it.
"""

import string

from nltk.corpus import words, names
from nltk.stem.wordnet import WordNetLemmatizer
from pdfminer.layout import LTAnno, LTChar
from pdfxml.me_extraction.me_consts import additional_words
from pdfxml.pdf_util.char_process import check_sorted_by_left, char_list2str


wnl = WordNetLemmatizer()
wl = set(words.words())
wl.update(additional_words)
name_set = set(names.words())
wl.update(name_set)


def max_word_split(char_list):
    """
    sort based on the left
    punctuation: comma, period, colon, semi-colon, parenthesis
    letters:

    if vertical overlap, should not be split into two parts.

    :param char_list:
    :return:
        char_list with LTAnno inserted.
    """
    if len(char_list) == 0:
        return []

    # only keep the LTChar
    char_list = [char for char in char_list if isinstance(char, LTChar)]

    # create the hor-overlapping constraints
    check_sorted_by_left(char_list)

    # get overlapping pairs as hard constraints
    pair_left_idx_list = []
    pair_right_idx_list = []
    for i in range(len(char_list)-1):
        if char_list[i].bbox[2] > char_list[i+1].bbox[0]:
            pair_left_idx_list.append(i)
            pair_right_idx_list.append(i+1)

    def is_word(start_i, end_i):
        """
        check whether the chars in the range is good
        :param start_i:
        :param end_i:
        :return:
        """
        # check the boundary
        if start_i in pair_right_idx_list or end_i in pair_left_idx_list:
            # very big penalty
            return -10000

        word = ""
        for char_idx in range(start_i, end_i+1):
            if len(char_list[char_idx].get_text()) > 1:
                return -1
            word += char_list[char_idx].get_text()

        # remove leading or trailing punctuation.
        word = word.strip(".,;:"+string.whitespace)
        word = word.lower()
        s_word = wnl.lemmatize(word, 'n')
        v_word = wnl.lemmatize(word, 'v')
        is_word = word in wl or s_word in wl or v_word in wl

        # special rule
        if len(word) == 1:
            if word in ['A', 'a']:
                return 1
            else:
                return -1

        #return 1 if is_word else -1
        if is_word:
            # give more weight to long
            return (end_i-start_i+1)*(end_i-start_i+1)
        else:
            return -1

    # dp[i] = dp[j] + word[i,j]
    # keep track of the split position.

    # use this for test
    "http://localhost:8080/pdf_viewer?pdf_name=10.1.1.6.2280_14"
    # dp[i] means with i char considerd
    dp = [-100000]*(len(char_list)+1)
    prev_end = [-1]*(len(char_list)+1)  # when previous end lead to -1, mean the last chunk
    dp[0] = 0
    for char_num in range(1, len(char_list)+1):
        for prev_char_num in range(0, char_num):
            word_score = is_word(prev_char_num, char_num-1)
            ms = 'word {}, score {}'.format(
                char_list2str([char_list[i] for i in range(prev_char_num, char_num)]),
                word_score)
            if dp[prev_char_num] + word_score > dp[char_num]:
                dp[char_num] = dp[prev_char_num] + word_score
                prev_end[char_num] = prev_char_num

    # recover the word here
    i = len(char_list)
    word_end_idx_list = []
    while i >= 0:
        word_end_idx_list.append(i-1)
        i = prev_end[i]
    print word_end_idx_list

    i = 0
    return_char_list = []
    while i < len(char_list):
        return_char_list.append(char_list[i])
        if i in word_end_idx_list:
            return_char_list.append(LTAnno(" "))
        i += 1
    return return_char_list

