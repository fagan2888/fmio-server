# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import requests
import rasterio
from celery import shared_task
from fmio import fmi, raster, forecast
from redis import StrictRedis

conn = StrictRedis()


def get_raw(url):
    r = requests.get(url, stream=True)
    r.raw.decode_content = True
    return r


def make_forecast(urls):
    filess = urls.apply(get_raw)
    A, B = filess.iloc[0], filess.iloc[1]
    with rasterio.open(A.raw) as a, rasterio.open(B.raw) as b:
        rasters = filess.copy()
        rasters.iloc[0] = a
        rasters.iloc[1] = b
        crops, translate, meta = raster.crop_rasters(rasters, **raster.DEFAULT_CORNERS)
    rrs = raster.raw2rr(crops)
    return forecast.forecast(rrs), meta


@shared_task(serializer='pickle')
def update_forecast(miner):
    with conn.lock(miner.id, timeout=miner.interval.total_seconds()*10):
        print("Checking if maps need updating.")
        urls = fmi.available_maps(resolution_scaling=0.7).tail(2)
        current_dates = urls.index
        print("Previous dates:", miner.previous_dates)
        print("Current dates:", current_dates)
        if len(current_dates) == len(miner.previous_dates) and all(current_dates == miner.previous_dates):
            print("No new maps, not updating.")
            return 0 # do nothing
        miner.previous_dates = current_dates
        print("New maps found, generating forecasts.")
        fcast, meta = make_forecast(urls)
        print("Saving generated forecasts.")
        png_paths = miner.save_frames(fcast, meta)
        miner.save_gif(png_paths)
        miner.swap_temps()
        print("Successfully updated maps.")
    return 1 # updated
