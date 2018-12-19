from pdfxml.debug_util import debug_info
from pdfxml.me_taxonomy.math_resources import func_name_list
PROJECT_FOLDER = None  # where all the python packages lie in

debug = True  # if debug == False, means deployment environment

debug_info("Should move the following words to math_resource")

math_words = [
    'w.r.t.', 's.t.',
]
math_words.extend(func_name_list)

additional_words = [
    'gcd',
    'i.e.', 'programme', 'lagrangian', 'optimality',
    'empirically', 'multi', 'regularizer', 'preprocessing',
    'two', 'of', 'by', 'whose', 'are', 'the',
    'bag-of-means', 'http', 'www', 'pinyin', 'html', 'model', 'performance',

    'minimum', 'estimator', 'well-known', 'mean-square',  # 2371_3
    'summation',  #2018_5

    # punctuation
    '.', ';'
]

# http://www.math.union.edu/~dpvc/jsmath/symbols/welcome.html
# all treated as math
math_font_key_list = ['MathematicalPi', 'GreekwithMathPi', "+MSBM"]
#
alphabeta_font_key_list = ["+CMSY", "+CMMI"]

special_nme_glyph_list = ['bullet',  'fi', 'ffi', 'fl']
# 'hyphen', removed because some ME might be mixed with plaintext with hypern

#ME_ANALYSIS_PARALLEL = True
ME_ANALYSIS_PARALLEL = False

CLW_OLD, CLW_FEB = range(2)
CLW_VERSION = CLW_FEB

min_word_len_thres = 3

SAME_BASE_LINE_CHECK = True  # enable the same baseline checking in the experiment
SUBSCRIPT_CHECK = True
ENABLE_SINGLE_CHAR = False  # enable after the word segmentation is finished


#ICST_USE_WHOLE_STAT = False  # use the whole document for statistics.
# march 10, run and check out the errors.
# The exclude by section is associated with the using whole doc
# when using whole doc, the abstract/reference might introduce noise
# to the font-value statistics.
ICST_USE_WHOLE_STAT = True # use the whole document for statistics.
EXCLUDE_BY_SECTION = True

DISABLE_ABBR_NME = True  # disable the Abbrevation as NME, as some ME are also in abbrevation.


###################
# The post processing include the sub expression matching
# the expansion based on the binary relations, equal, element
###################

# only for the statistical stage
SUB_EXP_MATCH_NO, \
    SUB_EXP_MATCH_SEQ,\
    SUB_EXP_MATCH_FLAT_2D_SEQ, \
    SUB_EXP_MATCH_2D = 0, 1, 2, 3

SUB_EXP_MATCH_V = SUB_EXP_MATCH_SEQ
#SUB_EXP_MATCH_V = SUB_EXP_MATCH_NO

CHAR_EQUAL_GN, CHAR_EQUAL_GN_FN = 0, 1
# only glyph name matching
# or both glyph name matching and font name matching
CHAR_EQUAL_V = CHAR_EQUAL_GN_FN

# TODO, what does expand mean?
EXPAND_ME = True

# Post Processing settings
ENABLE_POST_PROCESSING = True
SEQ_ME_MERGER = True
bin_weight = 1.0

#LANG_MODEL = True
LANG_MODEL = False

def me_ext_default_setting_lang():
    me_ext_single_page_baseline()
    # me_ext_single_page_baseline_bin()
    # me_ext_single_page_baseline_bin_sub()
    pass  # the default setting of adding all features.
    global EXCLUDE_BY_SECTION, ICST_USE_WHOLE_STAT, debug, bin_weight, \
        ENABLE_POST_PROCESSING, SEQ_ME_MERGER, LANG_MODEL
    if not ICST_USE_WHOLE_STAT:
        # only exclude when icst use whole doc is set
        EXCLUDE_BY_SECTION = False
    debug = False

    # debug = True  # for heuristic testing
    ENABLE_POST_PROCESSING = False
    # ENABLE_POST_PROCESSING = False
    if not ENABLE_POST_PROCESSING:
        SEQ_ME_MERGER = False
    # bin_weight = 1
    bin_weight = 0.5

    ENABLE_POST_PROCESSING = True
    SEQ_ME_MERGER = False
    LANG_MODEL = True


def me_ext_default_setting_no_lang():
    me_ext_single_page_baseline()
    # me_ext_single_page_baseline_bin()
    # me_ext_single_page_baseline_bin_sub()
    pass  # the default setting of adding all features.
    global EXCLUDE_BY_SECTION, ICST_USE_WHOLE_STAT, debug, bin_weight, \
        ENABLE_POST_PROCESSING, SEQ_ME_MERGER, LANG_MODEL
    if not ICST_USE_WHOLE_STAT:
        # only exclude when icst use whole doc is set
        EXCLUDE_BY_SECTION = False
    debug = False

    # debug = True  # for heuristic testing
    ENABLE_POST_PROCESSING = False
    # ENABLE_POST_PROCESSING = False
    if not ENABLE_POST_PROCESSING:
        SEQ_ME_MERGER = False
    # bin_weight = 1
    bin_weight = 0.5


def me_ext_default_setting():
    """
    The current setting of concern

    :return:
    """
    # the most simple model here
    me_ext_single_page_baseline()
    # me_ext_single_page_baseline_bin()
    # me_ext_single_page_baseline_bin_sub()
    pass  # the default setting of adding all features.
    global EXCLUDE_BY_SECTION, ICST_USE_WHOLE_STAT, debug, bin_weight, \
        ENABLE_POST_PROCESSING, SEQ_ME_MERGER, LANG_MODEL
    if not ICST_USE_WHOLE_STAT:
        # only exclude when icst use whole doc is set
        EXCLUDE_BY_SECTION = False
    debug = False

    # debug = True  # for heuristic testing
    ENABLE_POST_PROCESSING = False
    SEQ_ME_MERGER = False
    LANG_MODEL = False


def me_ext_fast_mode():
    """
    1. only get the pdf information once, page_num, page_size

    NO ILP based on enhancement.

    :return:
    """
    pass

#############
# based line, no expansion by binary, and no sub-matching
#############
def me_ext_single_page_baseline():
    """

    :return:
    """
    global SUB_EXP_MATCH_V, EXPAND_ME, ICST_USE_WHOLE_STAT
    SUB_EXP_MATCH_V = SUB_EXP_MATCH_NO
    EXPAND_ME = False
    ICST_USE_WHOLE_STAT = False


def me_ext_whole_doc_baseline():
    """

    :return:
    """
    global SUB_EXP_MATCH_V, EXPAND_ME, ICST_USE_WHOLE_STAT
    SUB_EXP_MATCH_V = SUB_EXP_MATCH_NO
    EXPAND_ME = False
    ICST_USE_WHOLE_STAT = True


#############
# based line + expand by binary op/rel
#############
def me_ext_single_page_baseline_bin():
    """

    :return:
    """
    global SUB_EXP_MATCH_V, EXPAND_ME, ICST_USE_WHOLE_STAT
    SUB_EXP_MATCH_V = SUB_EXP_MATCH_NO
    EXPAND_ME = True
    ICST_USE_WHOLE_STAT = False


def me_ext_whole_doc_baseline_bin():
    """

    :return:
    """
    global SUB_EXP_MATCH_V, EXPAND_ME, ICST_USE_WHOLE_STAT
    SUB_EXP_MATCH_V = SUB_EXP_MATCH_NO
    EXPAND_ME = True
    ICST_USE_WHOLE_STAT = True


#############
# based line + expand by binary op/rel + sub-matching
#############
def me_ext_single_page_baseline_bin_sub():
    """

    :return:
    """
    global SUB_EXP_MATCH_V, EXPAND_ME, ICST_USE_WHOLE_STAT
    SUB_EXP_MATCH_V = SUB_EXP_MATCH_SEQ
    EXPAND_ME = True
    ICST_USE_WHOLE_STAT = False


"""
def me_ext_set_use_whole():
    pass


def me_ext_set_use_whole_sub_match():
    pass


def me_ext_set_sub_matching():
    pass
"""