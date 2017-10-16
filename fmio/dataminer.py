import threading
import thread
from os import path, remove, listdir, makedirs, rename
from urllib import urlretrieve
from fmio import fmi
import time

download_extension = ".dl"


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
            for filename in listdir(self.tempdir):
                remove(path.join(self.tempdir, filename))

    def erase_extra_files(self):
        with self.lock:
            for filename in self.filenames()[self.stored_count:]:
                remove(path.join(self.tempdir, filename))

    def fetch_radar_data(self, ttime=None):
        """ttime is seconds since epoch, defaults to time.time()"""
        ttime = int(time.time() if ttime is None else ttime)
        thread.start_new_thread(_fetch, (self, ttime))

    def filenames(self):
        """Returns names of the stored files sorted as newest to oldest"""
        with self.lock:
            filenames = listdir(self.tempdir)
        filenames = filter(lambda x: not x.endswith(download_extension), filenames)
        filenames = map(int, filenames)
        filenames.sort(reverse=True)
        filenames = map(str, filenames)
        return filenames

    def filepaths(self):
        return map(lambda x: path.join(self.tempdir, x), self.filenames())

    def two_newest(self):
        filepaths = self.filepaths()
        return filepaths[0], filepaths[1]


def _fetch(miner, ttime):  # type: (DataMiner, float) -> None
    filename = str(ttime)
    download_filepath = path.join(miner.tempdir, filename+download_extension)
    url = fmi.gen_url(var='rr', timestamp=fmi.gen_timestamp(ttime))
    urlretrieve(url, filename=download_filepath)
    with miner.lock:
        rename(download_filepath, path.join(miner.tempdir, filename))
        miner.erase_extra_files()
