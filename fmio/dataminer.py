# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from fmio.storage import Storage
from redis import StrictRedis
import fmio.visualization as vis
from fmio import fmi, raster

conn = StrictRedis()


class DataMiner():
    def __init__(self, tempdir1, tempdir2, image_temp1, image_temp2):
        self.temps = [Storage(tempdir1), Storage(tempdir2)]
        self.png_storage = Storage(image_temp1)
        self.gif_storage = Storage(image_temp2)
        self.tempidx = 0
        self.previous_dates = []
        self.task_forecast = None
        self.id = 'forecaster'

    def swap_temps(self):
        with conn.lock('temp_swap'):
            self.tempidx = (self.tempidx + 1) % len(self.temps)

    def current_temp(self):
        return self.temps[self.tempidx]

    def download_temp(self):
        return self.temps[(self.tempidx + 1) % len(self.temps)]

    def save_frames(self, fcast, meta):
        png_paths = fcast.copy()
        self.download_temp().remove_all_files()
        self.png_storage.remove_all_files()
        for t, fc in fcast.iteritems():
            tiffpath = self.download_temp().path(t.strftime(fmi.FNAME_FORMAT))
            raster.write_rr_geotiff(fc, meta, tiffpath)
            png_name = t.strftime(fmi.FNAME_TIME_FORMAT) + '.png'
            png_path = self.png_storage.path(png_name)
            vis.tif_to_png(tiffpath, png_path, crop='metrop')
            png_paths[t] = png_path
        return png_paths

    def save_gif(self, png_paths):
        with conn.lock('gif_swap'):
            self.gif_storage.remove_all_files()
            vis.pngs2gif(png_paths, self.gif_storage.path('forecast.gif'))
