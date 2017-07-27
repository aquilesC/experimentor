import sys
import datetime

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