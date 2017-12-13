# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import rasterio
import imageio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os import path
from fmio import fmi, basemap, forecast, raster
from fmio import visualization as vis
from j24 import home, ensure_join

plt.close('all')


def crop_and_plot(f):
    radar = rasterio.open(f)
    ax = border.to_crs(radar.read_crs().data).plot(zorder=0)
    windowed, transwin, meta = raster.crop_raster(radar, x0=x0, y0=y0, x1=x1, y1=y1)
    rasterio.plot.show(windowed, transform=transwin, ax=ax, zorder=10)


def plot_box_map(radar, border, box):
    ax = fmi.plot_radar_map(radar, border=border)
    basemap.plot_edge(box, ax=ax, zorder=10)
    ax.set_xlim(left=1e4, right=7.8e5)
    ax.set_ylim(top=7.8e6, bottom=6.45e6)


def plot_files(paths, **kws):
    for p in paths.values:
        plt.figure()
        fmi.plot_radar_file(p, **kws)


def rr_series_at_coords(raster_paths, x=3.5e5, y=6.65e6):
    rvals = raster_paths.copy()
    for t, rp in raster_paths.iteritems():
        with rasterio.open(rp, 'r') as ras:
            rvals[t] = raster.rr_at_coords(ras, x, y)


def plot_rr_series(rrs, **kws):
    ax = rrs.plot(**kws)
    ax.set_ylabel('Intensity mm/h')
    return ax


if __name__ == '__main__':
    t_range = dict(starttime='2017-10-12T07:00:00Z', endtime='2017-10-12T08:30:00Z')

    cities = basemap.cities()
    border = basemap.border()

    x0=1.1e5
    y0=6.55e6
    x1=6.5e5
    y1=7e6
    #urls = fmi.available_maps(**t_range)
    fakeindex = pd.DatetimeIndex(freq='5min', start=t_range['starttime'], end=t_range['endtime'])
    urls = pd.Series(index=fakeindex) # fake urls
    #url = fmi.gen_url(timestamp='2017-10-17T07:00:00Z')
    dl = fmi.available_maps().tail(2)
    #fmi.download_maps(urls)
    paths = fmi.download_maps(dl)
    savedir = ensure_join(home(), 'results', 'sataako')

    ### FORECAST AND SAVE LOGIC ###
    rads = paths.apply(rasterio.open)
    crops, tr, meta = raster.crop_rasters(rads, **raster.DEFAULT_CORNERS)
    dtype = meta['dtype']
    rad_crs = rads.iloc[0].read_crs().data
    rads.apply(lambda x: x.close())
    rr = raster.raw2rr(crops)
    fcast = forecast.forecast(rr)
    savepaths = fcast.copy()
    pngpaths = fcast.copy()
    for t, fc in fcast.iteritems():
        savepath = path.join(savedir, t.strftime(fmi.FNAME_FORMAT))
        savepaths.loc[t] = savepath
        raster.write_rr_geotiff(fc, meta, savepath)
    #################################
        fname = t.strftime(fmi.FNAME_TIME_FORMAT) + '.png'
        pngpath = path.join(savedir, 'png', fname)
        pngpaths[t] = pngpath
        vis.plot_save_rr(fc, tr, border, rad_crs, pngpath)
        plt.close()

    with rasterio.open(savepath, 'r') as savedraster:
        rate = raster.raw2rr(savedraster.read(1))
        ax = vis.plot_save_rr(rate, tr, border, rad_crs, path.join(savedir, 'test.png'))
        plt.close()


    gifpath = path.join(savedir, 'forecast.gif')
    #vis.pngs2gif(pngpaths, gifpath)

    #v = forecast.motion(rru[0], rru[1])
    #out = forecast.forecast()

    #plot_save_rr(rr[0], tr, border, rad_crs, 'in0.png')
    #plot_save_rr(rr[1], tr, border, rad_crs, 'in1.png')
    #plot_save_rr(out, tr, border, rad_crs, 'out.png')

    f = paths.iloc[0]
    box = basemap.box(**raster.DEFAULT_CORNERS)

    #rad = paths.apply(rasterio.open)



