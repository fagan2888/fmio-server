# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import requests
import rasterio
from fmio import raster, forecast


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



