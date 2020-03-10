# -*- coding: utf-8 -*-
"""
    logger_with_time
    ================
    Workaround for implementing a logging strategy both with saving to file and with output with time for packages and
    scripts that use a lot of print and not use the logging package.
    Since version 0.2 of Experimentor, the logging was implemented almost everywhere.

    .. depectrated:: v0.2

    .. sectionauthor:: Aquiles Carattino <aquiles@uetke.com>
"""
import datetime
import sys


class logger:
    def __init__(self, file=None):
        if file is not None:
            self.file = open(file, 'a')
            self.write_to_file = True
        else:
            self.write_to_file = False

        self.old_stdout = sys.stdout

    def write(self, x):
        x = x.rstrip()
        if len(x) == 0: return
        self.old_stdout.write('%s - %s\n' % (datetime.datetime.now(), x))
        if self.write_to_file:
            self.file.write('%s - %s\n' % (datetime.datetime.now(), x))

    def flush(self):
        if self.write_to_file:
            self.file.flush()
        else:
            pass