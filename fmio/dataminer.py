import threading

import requests
from pandas.core.generic import NDFrame

from fmio import fmi
from fmio.storage import Storage
from fmio.timer import TimedTask


class DataMiner(TimedTask):
    def __init__(self, tempdir1, tempdir2, interval_mins=5):
        TimedTask.__init__(self, interval_mins=interval_mins)
        self.temps = [Storage(tempdir1), Storage(tempdir2)]
        self.temp_swap_lock = threading.RLock()
        self.tempidx = 0

    def swap_temps(self):
        with self.temp_swap_lock:
            self.tempidx = (self.tempidx + 1) % len(self.temps)

    def current_temp(self):
        return self.temps[self.tempidx]

    def download_temp(self):
        return self.temps[(self.tempidx + 1) % len(self.temps)]

    def update_maps(self):
        urls = fmi.available_maps().tail(2)  # type: NDFrame

        def get_file(t):
            dtime, url = t
            r = requests.get(url, stream=True)
            r.raw.decode_content = True
            return dtime, r

        files = map(get_file, urls.iteritems())
        self.download_temp().remove_all_files()
        for t in files:
            dtime, r = t
            # DO EXTRAPOLATION HERE
            # with rasterio.open(t[1].raw) as data:
            #    print(data.read(1))
            with open(self.download_temp().path(dtime.strftime(fmi.FNAME_FORMAT)), mode="w+b") as f:
                for chunk in r:
                    f.write(chunk)

        self.swap_temps()

    def timed_task(self):
        self.update_maps()
