# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
from matplotlib import colors
from rasterio.plot import show

plt.close('all')
plt.ion()

with open('api.key', 'r') as keyfile:
    key = keyfile.readline()
radurl_base = 'http://wms.fmi.fi/fmi-apikey/{}/geoserver/Radar/ows?service=WMS&request=GetMap&format=image/geotiff&bbox=-118331.366,6335621.167,875567.732,7907751.537&width=1700&height=2500&srs=EPSG:3067&layers=Radar:suomi_dbz_eureffin'
radurl = radurl_base.format(key)
rad = 'Radar-suomi_dbz_eureffin.tif'
world = gpd.read_file('ne_10m_admin_0_countries.shp')
finland = world[world.ADMIN=='Finland']

data = rasterio.open('Radar-suomi_dbz_eureffin.tif')
dat = data.read(1)
mask = dat==252
d = dat.copy()
d[mask] = 0
datm = np.ma.MaskedArray(data=d, mask=d==0)
nummask = np.ma.MaskedArray(data=dat, mask=~mask)

cmap=colors.ListedColormap([(0.5,0.6,0.2,0.9)])

ax = finland.to_crs(data.read_crs().data).plot(zorder=0, color='gray')

show(datm, transform=data.transform, ax=ax, zorder=3)
show(nummask, transform=data.transform, ax=ax, zorder=4, alpha=.1, interpolation='bilinear')
ax.axis('off')
ax.set_xlim(left=-5e4)
ax.set_ylim(top=7.8e6, bottom=6.42e6)
