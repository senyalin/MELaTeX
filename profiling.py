
############
# set up the during recorder
############
import time
from pdfxml.loggers import profiling_logger


class DurationRecorder(object):
    """
    only for sequential execution
    """
    def __init__(self):
        self.logger_list = []
        self.beg_time = None
        self.task_name = None

    def add_logger(self, logger):
        self.logger_list.append(logger)

    def begin_timer(self, task_name):
        # first log if with previous task
        if self.task_name is not None:
            cur_time = time.time()
            for logger in self.logger_list:
                logger.info("Task {} take {} seconds".format(
                    self.task_name, cur_time-self.beg_time))

        self.beg_time = time.time()
        self.task_name = task_name


global_duration_recorder = None
def get_global_duration_recorder():
    global global_duration_recorder
    if global_duration_recorder is None:
        global_duration_recorder = DurationRecorder()
        global_duration_recorder.add_logger(profiling_logger)
    return global_duration_recorder
