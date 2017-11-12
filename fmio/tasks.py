# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import requests
import rasterio
from celery import shared_task
from fmio import fmi, raster, forecast
import fmio.visualization as vis
from sherlock import Lock


@shared_task(track_started=True, serializer='pickle')
def update_forecast(miner):
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
    miner.download_temp().remove_all_files()
    miner.png_storage.remove_all_files()
    for t, fc in fcast.iteritems():
        savepath = miner.download_temp().path(t.strftime(fmi.FNAME_FORMAT))
        raster.write_rr_geotiff(fc, meta, savepath)
        png_name = t.strftime(fmi.FNAME_TIME_FORMAT) + '.png'
        png_path = miner.png_storage.path(png_name)
        vis.tif_to_png(savepath, png_path, crop='metrop')
        png_paths[t] = png_path
    with Lock('gif_swap'):
        miner.gif_storage.remove_all_files()
        vis.pngs2gif(png_paths, miner.gif_storage.path('forecast.gif'))
    miner.swap_temps()
    print("Successfully updated maps.")
    return 1 # updated