# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import threading

import requests
from pandas.core.generic import NDFrame

from fmio import fmi
from fmio.storage import Storage
from fmio.timer import TimedTask
import datetime
import pytz
import pandas


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
        print("Checking if maps need updating.")
        urls = fmi.available_maps().tail(2)  # type: NDFrame
        dates = map(lambda x: datetime.datetime.strptime(x, fmi.FNAME_FORMAT), self.current_temp().filenames())
        dates = map(lambda x: x.replace(tzinfo=pytz.UTC), dates)
        dates.sort()
        for d in dates[-1:]:
            d = pandas.Timestamp(d)
            print(d, urls.tail(1).keys()[0])
            if d >= urls.tail(1).keys()[0]:
                print("No new maps, not updating.")
                return

        print("New maps found, updating.")

        def get_file(t):
            dtime, url = t
            r = requests.get(url, stream=False)
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
        print("Successfully updated maps.")

    def timed_task(self):
        try:
            self.update_maps()
        except Exception as e:
            print("Got an unexpected exception, ignoring:", e.message)
