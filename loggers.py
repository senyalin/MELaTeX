"""
try to initialize a bunch of loggers here

This page describe a very good common practice:
https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

https://en.wikipedia.org/wiki/YAML

"""

import os
import sys
import logging
import logging.handlers
import logging.config
from pdfxml.path_util import SHARED_FOLDER

# create the log folder if not exist
logger_folder = "{}/logs".format(SHARED_FOLDER)
if not os.path.isdir(logger_folder):
    os.makedirs(logger_folder)


def setup_logger(name, log_file, level=logging.DEBUG):
    """
    Function setup as many loggers as you want
    https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings

    :param name:
    :param log_file:
    :param level:
    :return:
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    if log_file is None:
        handler = logging.StreamHandler(sys.stdout)
    elif log_file == 'null':
        handler = logging.NullHandler()
    else:
        from file_util import test_folder_exist_for_file_path
        test_folder_exist_for_file_path(log_file)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


# set up many logger here
general_logger = setup_logger(
    'general_logger',
    None,
    logging.DEBUG
)


pdf_util_error_log = setup_logger(
    'pdf_util_error_log',
    '{}/pdf_util_error.log'.format(logger_folder),
    logging.ERROR
)


pdf_util_debug_log = setup_logger(
    'pdf_util_debug_log',
    '{}/pdf_util_debug.log'.format(logger_folder),
    logging.DEBUG
)


me_extraction_logger = setup_logger(
    'me_extraction_logger',
    '{}/me_extraction.log'.format(logger_folder),
    logging.DEBUG
)


me_extraction_error_logger = setup_logger(
    'me_extraction_error_logger',
    '{}/me_extraction_error.log'.format(logger_folder),
    logging.ERROR
)


# NOTE: change to Null Handler due to too much information.
doc_layout_logger = setup_logger(
    'doc_layout_logger',
    #None,
    '{}/doc_layout.log'.format(logger_folder),
    logging.DEBUG
)


me_parsing_logger = setup_logger(
    'me_parsing_logger',
    '{}/me_parsing.log'.format(logger_folder),
    logging.DEBUG
)


profiling_logger = setup_logger(
    'profiling_logger',
    '{}/profiling.log'.format(logger_folder),
    logging.DEBUG
)


me_analysis_logger = setup_logger(
    'me_analysis_logger',
    '{}/me_analysis.log'.format(logger_folder),
    logging.DEBUG
)