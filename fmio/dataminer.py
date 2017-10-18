import thread
import time
from os import path, remove, rename
from urllib import urlretrieve

from fmio import storage
from fmio import fmi

download_extension = ".dl"


class DataMiner(storage.Storage):
    def __init__(self, tempdir, stored_count=6):
        storage.Storage.__init__(self, tempdir)
        self.stored_count = stored_count

    def erase_extra_files(self):
        with self.lock:
            for filename in self.filenames()[self.stored_count:]:
                remove(path.join(self.tempdir, filename))

    def fetch_radar_data(self, ttime=None):
        """ttime is seconds since epoch, defaults to time.time()"""
        ttime = int(time.time() if ttime is None else ttime)
        thread.start_new_thread(_fetch, (self, ttime))


def _fetch(miner, ttime):  # type: (DataMiner, float) -> None
    filename = str(ttime)
    download_filepath = path.join(miner.tempdir, filename + download_extension)
    url = fmi.gen_url(timestamp=fmi.gen_timestamp(ttime))
    urlretrieve(url, filename=download_filepath)
    with miner.lock:
        rename(download_filepath, path.join(miner.tempdir, filename))
        miner.erase_extra_files()
