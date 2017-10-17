# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import shapely
import rasterio
import rasterio.mask
import matplotlib.pyplot as plt
from fmio import fmi, basemap

def plot_files(paths, **kws):
    for p in paths.values:
        plt.figure()
        fmi.plot_radar_file(p, **kws)

t_range = dict(starttime='2017-10-11T07:00:00Z', endtime='2017-10-11T07:30:00Z')

cities = basemap.cities()
border = basemap.border()

urls = fmi.available_maps(**t_range)
url = fmi.gen_url(timestamp='2017-10-17T07:00:00Z')
dl = urls.tail(2)
#paths = fmi.download_maps(dl)
f = paths.iloc[0]
box = basemap.box()
radar = rasterio.open(f)
#ax = fmi.plot_radar_map(radar)
#basemap.plot_edge(box, ax=ax, zorder=10)
pol=shapely.geometry.geo.mapping(box[0])
shapes=[pol]
cropped, transf = rasterio.mask.mask(radar, shapes=shapes, nodata=fmi.RR_NODATA, crop=True)
meta = radar.meta.copy()
ax = border.to_crs(radar.read_crs().data).plot(zorder=0)
rasterio.plot.show(cropped, transform=transf, ax=ax, zorder=10)
ax.set_xlim(left=1e4, right=7.8e5)
ax.set_ylim(top=7.8e6, bottom=6.45e6)
#rad = paths.apply(rasterio.open)



