# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import rasterio
import matplotlib.pyplot as plt
from os import path
from fmio import fmi, basemap, forecast, raster
from j24 import home, ensure_join

plt.close('all')



def plot_save_rr(rr, transform, border, fname):
    ax = border.to_crs(rad_crs).plot(zorder=0)
    raster.plot_rr(rr, transform=transform, ax=ax, zorder=10)
    ax.set_axis_off()
    ax.get_figure().savefig(path.join(savedir, fname), bbox_inches='tight')
    return ax


def crop_and_plot(f):
    radar = rasterio.open(f)
    ax = border.to_crs(radar.read_crs().data).plot(zorder=0)
    windowed, transwin = raster.crop_raster(radar, x0=x0, y0=y0, x1=x1, y1=y1)
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


t_range = dict(starttime='2017-10-12T07:00:00Z', endtime='2017-10-12T08:30:00Z')

cities = basemap.cities()
border = basemap.border()

x0=1.1e5
y0=6.55e6
x1=6.5e5
y1=7e6
urls = fmi.available_maps(**t_range)
#url = fmi.gen_url(timestamp='2017-10-17T07:00:00Z')
dl = urls.tail(2)
#fmi.download_maps(urls)
#paths = fmi.download_maps(dl)
rads = paths.apply(rasterio.open)
rad_crs = rads.iloc[0].read_crs().data
rr = []
rru = []
for rad in rads.values:
    cropped, tr = raster.crop_raster(rad, x0, y0, x1, y1)
    rate = cropped*0.01
    rr.append(rate)
    rru.append(forecast.rr2ubyte(rate))
#v = forecast.motion(rru[0], rru[1])
out = forecast.extrapolate(rr[1], v, 1)

savedir = ensure_join(home(), 'results', 'sataako')

plot_save_rr(rr[0], tr, border, 'in0.png')
plot_save_rr(rr[1], tr, border, 'in1.png')
plot_save_rr(out, tr, border, 'out.png')

f = paths.iloc[0]
box = basemap.box(x0=x0, y0=y0, x1=x1, y1=y1)



#rad = paths.apply(rasterio.open)



