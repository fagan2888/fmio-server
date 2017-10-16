import threading
from os import path, remove, listdir, makedirs
from urllib import urlretrieve
from fmio import fmi
import time


class DataMiner:
    def __init__(self, tempdir, stored_count=6):
        self.stored_count = stored_count
        self.tempdir = tempdir
        self.lock = threading.RLock()
        with self.lock:
            if not path.exists(self.tempdir):
                makedirs(self.tempdir)
            self.remove_all_files()

    def remove_all_files(self):
        with self.lock:
            for filename in self.filenames():
                remove(path.join(self.tempdir, filename))

    def erase_extra_files(self):
        with self.lock:
            for filename in self.filenames()[self.stored_count:]:
                remove(path.join(self.tempdir, filename))

    def fetch_radar_data(self, ttime=None):
        """ttime is seconds since epoch, defaults to time.time()"""
        ttime = int(ttime or time.time())
        with self.lock:
            filepath = path.join(self.tempdir, str(ttime))
            urlretrieve(fmi.gen_url(var='rr', timestamp=fmi.gen_timestamp(ttime)), filename=filepath)
            self.erase_extra_files()

    def filenames(self):
        """Returns names of the stored files sorted as newest to oldest"""
        with self.lock:
            filenames = listdir(self.tempdir)
            filenames = map(int, filenames)
            filenames.sort(reverse=True)
            filenames = map(str, filenames)
            return filenames
