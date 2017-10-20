# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import numpy as np
import pandas as pd
import rasterio
import pyproj
from fmio import fmi
import datetime
import pytz

DBZ_NODATA = 255
RR_NODATA = 65535
RR_FACTOR = 100
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


def value_at_coords(raster, x, y, band=1):
    """value at raster native coordinate system"""
    gen = raster.sample(xy=[(x, y)], indexes=band)
    return gen.next()[0]


def rr_at_coords(*args, **kws):
    """rainrate at raster native coordinate system"""
    return raw2rr(value_at_coords(*args, **kws))


def crop_rasters(rasters, x0=DEFAULT_CORNERS['x0'], y0=DEFAULT_CORNERS['y0'],
                 x1=DEFAULT_CORNERS['x1'], y1=DEFAULT_CORNERS['y1']):
    crops = []
    for raster in rasters.values:
        cropped, transform, meta = crop_raster(raster, x0, y0, x1, y1)
        crops.append(cropped)
    return pd.Series(index=rasters.index, data=crops), transform, meta


def write_rr_geotiff(rr, meta, savepath):
    with rasterio.open(savepath, 'w', **meta) as dest:
        dest.write_band(1, rr2raw(rr, dtype=meta['dtype']))


def plot_radar_map(raster, border=None, cities=None, ax=None, crop='fi'):
    dat = raster.read(1)
    mask = dat==RR_NODATA
    d = raw2rr(dat.copy())
    d[mask] = 0
    datm = np.ma.MaskedArray(data=d, mask=d==0)
    nummask = np.ma.MaskedArray(data=dat, mask=~mask)
    ax = rasterio.plot.show(datm, transform=raster.transform, ax=ax, zorder=3)
    rasterio.plot.show(nummask, transform=raster.transform, ax=ax,
                       zorder=4, alpha=.1, interpolation='bilinear')
    if border is not None:
        border.to_crs(raster.read_crs().data).plot(zorder=0, color='gray',
                                                       ax=ax)
    if cities is not None:
        cities.to_crs(raster.read_crs().data).plot(zorder=5, color='black',
                                                       ax=ax, markersize=2)
    ax.axis('off')
    if crop=='fi':
        ax.set_xlim(left=1e4, right=7.8e5)
        ax.set_ylim(top=7.8e6, bottom=6.45e6)
    elif crop=='metrop': # metropolitean area TODO
        ax.set_xlim(left=1e4, right=7.8e5)
        ax.set_ylim(top=7.8e6, bottom=6.45e6)
    else:
        ax.set_xlim(left=-5e4)
        ax.set_ylim(top=7.8e6, bottom=6.42e6)
    return ax


def plot_radar_file(radarfilepath, **kws):
    with rasterio.open(radarfilepath) as radar_data:
        return plot_radar_map(radar_data, **kws)


def raw2rr(raw):
    return raw/RR_FACTOR


def rr2raw(rr, dtype='uint16'):
    rr_filled = rr.copy()
    rr_filled[np.isnan(rr)] = 0
    scaled = rr_filled*RR_FACTOR
    return scaled.round().astype(dtype)

def lonlat_to_xy(lon, lat):
    p1 = pyproj.Proj(init='epsg:4326')
    p2 = pyproj.Proj(init='epsg:3067')
    xy = pyproj.transform(p1, p2, lon, lat)
    return xy

def filename_to_datestring(filename):
    dtime = datetime.datetime.strptime(filename, fmi.FNAME_FORMAT).replace(tzinfo=pytz.UTC)
    stime = dtime.strftime(fmi.TIME_FORMAT)
    return stime
