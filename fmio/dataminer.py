# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import threading
import requests
import datetime
import pytz
import pandas
import rasterio
from fmio import fmi, raster, forecast
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
        print("Checking if maps need updating.")
        urls = fmi.available_maps().tail(2)
        dates = map(lambda x: datetime.datetime.strptime(x, fmi.FNAME_FORMAT), self.current_temp().filenames())
        dates = map(lambda x: x.replace(tzinfo=pytz.UTC), dates)
        dates.sort()
        for d in dates[-1:]:
            d = pandas.Timestamp(d)
            print(d, urls.tail(1).keys()[0])
            if d >= urls.tail(1).keys()[0]:
                print("No new maps, not updating.")
                return

        print("New maps found, generating forecasts.")

        def get_raw(url):
            r = requests.get(url, stream=True)
            r.raw.decode_content = True
            return r

        filess = urls.apply(get_raw)
        A, B = filess.iloc[0], filess.iloc[1]
        with rasterio.open(A.raw) as a, rasterio.open(B.raw) as b:
            rasters = filess.copy()
            rasters.iloc[0] = a
            rasters.iloc[1] = b
            crops, translate, meta = raster.crop_rasters(rasters, **raster.DEFAULT_CORNERS)
        rrs = raster.raw2rr(crops)
        fcast = forecast.forecast(rrs)

        print("Saving generated forecasts.")
        self.download_temp().remove_all_files()
        for t, fc in fcast.iteritems():
            savepath = self.download_temp().path(t.strftime(fmi.FNAME_FORMAT))
            raster.write_rr_geotiff(fc, meta, savepath)
        self.swap_temps()

        print("Successfully updated maps.")

    def timed_task(self):
        try:
            self.update_maps()
        except Exception as e:
            print("Got an unexpected exception, ignoring:", e.message, e.args)
