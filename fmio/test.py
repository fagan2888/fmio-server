# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import shapely
import rasterio
import rasterio.mask
#import georaster
import matplotlib.pyplot as plt
from fmio import fmi, basemap

plt.close('all')

def crop_raster(raster, x0, y0, x1, y1):
    win = rasterio.windows.from_bounds(left=x0, bottom=y0, right=x1, top=y1,
                                       transform=raster.transform)
    transwin = rasterio.windows.transform(window=win,
                                          transform=raster.transform)
    windowed = raster.read(1, window=win)
    return windowed, transwin


def plot_files(paths, **kws):
    for p in paths.values:
        plt.figure()
        fmi.plot_radar_file(p, **kws)


t_range = dict(starttime='2017-10-12T07:00:00Z', endtime='2017-10-12T07:30:00Z')

cities = basemap.cities()
border = basemap.border()

x0=1.1e5
y0=6.55e6
x1=6.5e5
y1=7e6
urls = fmi.available_maps(**t_range)
url = fmi.gen_url(timestamp='2017-10-17T07:00:00Z')
dl = urls.tail(2)
#paths = fmi.download_maps(dl)
rads = paths.apply(rasterio.open)
crops = []
trans = []
for i, rad in enumerate(rads.values):
    cropped, tr = crop_raster(rad, x0, y0, x1, y1)
    crops.append(cropped)
    trans.append(tr)
f = paths.iloc[0]
box = basemap.box(x0=x0, y0=y0, x1=x1, y1=y1)
radar = rasterio.open(f)
ax = fmi.plot_radar_map(radar, border=border)
basemap.plot_edge(box, ax=ax, zorder=10)
#pol = shapely.geometry.geo.mapping(box[0])
#shapes = [pol]
#cropped, transf = rasterio.mask.mask(radar, shapes=shapes, nodata=1000, crop=True)
#meta = radar.meta.copy()
ax = border.to_crs(radar.read_crs().data).plot(zorder=0)
windowed, transwin = crop_raster(radar, x0=x0, y0=y0, x1=x1, y1=y1)
rasterio.plot.show(windowed, transform=transwin, ax=ax, zorder=10)
ax.set_xlim(left=1e4, right=7.8e5)
ax.set_ylim(top=7.8e6, bottom=6.45e6)
#rad = paths.apply(rasterio.open)



