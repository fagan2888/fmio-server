# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import threading
import requests
import rasterio
from fmio import fmi, raster, forecast
import fmio.visualization as vis
from fmio.storage import Storage
from fmio.timer import TimedTask


class DataMiner(TimedTask):
    def __init__(self, tempdir1, tempdir2, image_temp1, image_temp2, interval_mins=5):
        TimedTask.__init__(self, interval_mins=interval_mins)
        self.temps = [Storage(tempdir1), Storage(tempdir2)]
        self.temp_swap_lock = threading.RLock()
        self.gif_swap_lock = threading.RLock()
        self.png_storage = Storage(image_temp1)
        self.gif_storage = Storage(image_temp2)
        self.tempidx = 0
        self.previous_dates = []

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
        current_dates = urls.index
        print("Previous dates:", self.previous_dates)
        print("Current dates:", current_dates)
        if len(current_dates) == len(self.previous_dates) and all(current_dates == self.previous_dates):
            print("No new maps, not updating.")
            return
        self.previous_dates = current_dates

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
        png_paths = fcast.copy()
        self.download_temp().remove_all_files()
        self.png_storage.remove_all_files()
        for t, fc in fcast.iteritems():
            savepath = self.download_temp().path(t.strftime(fmi.FNAME_FORMAT))
            raster.write_rr_geotiff(fc, meta, savepath)
            png_name = t.strftime(fmi.FNAME_TIME_FORMAT) + '.png'
            png_path = self.png_storage.path(png_name)
            vis.tif_to_png(savepath, png_path, crop='metrop')
            png_paths[t] = png_path
        with self.gif_swap_lock:
            self.gif_storage.remove_all_files()
            vis.pngs2gif(png_paths, self.gif_storage.path('forecast.gif'))
        self.swap_temps()

        print("Successfully updated maps.")

    def timed_task(self):
        #try:
            self.update_maps()
        #except Exception as e:
        #    print("Got an unexpected exception, ignoring:", e.message)
