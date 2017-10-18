import threading
from os import path, remove, listdir, makedirs


class Storage:
    def __init__(self, tempdir):
        self.tempdir = tempdir
        self.lock = threading.RLock()
        with self.lock:
            if not path.exists(self.tempdir):
                makedirs(self.tempdir)
            self.remove_all_files()

    def remove_all_files(self):
        with self.lock:
            for filename in listdir(self.tempdir):
                remove(path.join(self.tempdir, filename))

    def filenames(self):
        """Returns names of the stored files sorted as newest to oldest"""
        with self.lock:
            filenames = listdir(self.tempdir)

        def represents_int(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        filenames = filter(lambda x: not represents_int(x), filenames)
        filenames = map(int, filenames)
        filenames.sort(reverse=True)
        filenames = map(str, filenames)
        return filenames

    def filepaths(self):
        return map(lambda x: path.join(self.tempdir, x), self.filenames())

    def two_newest(self):
        filepaths = self.filepaths()
        return filepaths[0], filepaths[1]

    def path(self, filename=""):
        return path.join(self.tempdir, filename)
