# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import numpy as np
import rasterio


def mask_rr(rr):
    """Mask low and nan rainrate values."""
    mask = np.bitwise_or(np.isnan(rr), rr<0.05)
    return np.ma.masked_where(mask, rr)


def plot_rr(rr, cmap='jet', vmin=0.05, vmax=10, **kws):
    """Plot rainrate raster."""
    rr_masked = mask_rr(rr)
    return rasterio.plot.show(rr_masked, cmap=cmap, vmin=vmin, vmax=vmax, **kws)


def crop_raster(raster, x0, y0, x1, y1):
    win = rasterio.windows.from_bounds(left=x0, bottom=y0, right=x1, top=y1,
                                       transform=raster.transform)
    transwin = rasterio.windows.transform(window=win,
                                          transform=raster.transform)
    windowed = raster.read(1, window=win)
    return windowed, transwin

