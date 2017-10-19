# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import numpy as np
import pandas as pd
import rasterio
from fmio import fmi


DEFAULT_CORNERS = dict(x0=1.1e5, y0=6.55e6, x1=6.5e5, y1=7e6)


def mask_rr(rr):
    """Mask low and nan rainrate values."""
    mask = np.bitwise_or(np.isnan(rr), rr<0.05)
    return np.ma.masked_where(mask, rr)


def plot_rr(rr, cmap='jet', vmin=0.05, vmax=10, **kws):
    """Plot rainrate raster."""
    rr_masked = mask_rr(rr)
    return rasterio.plot.show(rr_masked, cmap=cmap, vmin=vmin, vmax=vmax, **kws)


def crop_raster(raster, x0=DEFAULT_CORNERS['x0'], y0=DEFAULT_CORNERS['y0'],
                x1=DEFAULT_CORNERS['x1'], y1=DEFAULT_CORNERS['y1']):
    win = rasterio.windows.from_bounds(left=x0, bottom=y0, right=x1, top=y1,
                                       transform=raster.transform)
    transform = rasterio.windows.transform(window=win,
                                           transform=raster.transform)
    cropped = raster.read(1, window=win)
    meta = raster.meta.copy()
    meta.update(dict(driver='GTiff',
                     height=cropped.shape[0],
                     width=cropped.shape[1],
                     transform=transform))
    return cropped, transform, meta


def crop_rasters(rasters, x0=DEFAULT_CORNERS['x0'], y0=DEFAULT_CORNERS['y0'],
                 x1=DEFAULT_CORNERS['x1'], y1=DEFAULT_CORNERS['y1']):
    crops = []
    for raster in rasters.values:
        cropped, transform, meta = crop_raster(raster, x0, y0, x1, y1)
        crops.append(cropped)
    return pd.Series(index=rasters.index, data=crops), transform, meta


def write_rr_geotiff(rr, meta, savepath):
    with rasterio.open(savepath, 'w', **meta) as dest:
        dest.write_band(1, fmi.rr2raw(rr, dtype=meta['dtype']))


def plot_radar_file(radarfilepath, **kws):
    with rasterio.open(radarfilepath) as radar_data:
        return fmi.plot_radar_map(radar_data, **kws)


