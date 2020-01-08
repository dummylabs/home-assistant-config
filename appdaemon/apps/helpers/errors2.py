import logging
from contextlib import ContextDecorator

class report_errors_to(ContextDecorator):
    def __init__(self, messenger):
        self.messenger = messenger
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        if exc[0]:
            app_id = sys._getframe(2).f_globals['__file__']
            self.messenger.alert("{}: {} in {}, see log for details".format(exc[0].__name__, exc[1], app_id))