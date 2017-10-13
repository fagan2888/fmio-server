# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import urlencode
from rasterio.plot import show

def read_key(keyfilepath):
    with open(keyfilepath, 'r') as keyfile:
        return keyfile.readline().splitlines()[0]


def gen_url(*args, width=3400, height=5380, **kws):
    key = read_key(*args, **kws)
    url_base = 'http://wms.fmi.fi/fmi-apikey/{}/geoserver/Radar/ows?'.format(key)
    params = dict(service='WMS',
                  version='1.3.0',
                  request='GetMap',
                  layers='Radar:suomi_dbz_eureffin',
                  styles='raster',
                  bbox='-118331.366,6335621.167,875567.732,7907751.537',
                  srs='EPSG:3067',
                  format='image/geotiff',
                  width=width,
                  height=height)
    # old API params
    params_old = dict(service='WMS',
                      request='GetMap',
                      format='image/geotiff',
                      bbox='-118331.366,6335621.167,875567.732,7907751.537',
                      width=1700,
                      height=2500,
                      srs='EPSG:3067',
                      layers='Radar:suomi_dbz_eureffin')
    return url_base + urlencode(params)


def plot_radar_map(radar_data, border, cities=None, ax=None):
    dat = radar_data.read(1)
    mask = dat==255
    d = dat.copy()
    d[mask] = 0
    datm = np.ma.MaskedArray(data=d, mask=d==0)
    nummask = np.ma.MaskedArray(data=dat, mask=~mask)
    ax = border.to_crs(radar_data.read_crs().data).plot(zorder=0, color='gray')
    if cities is not None:
        cities.to_crs(radar_data.read_crs().data).plot(zorder=5, color='black',
                                                       ax=ax, markersize=2)
    show(datm, transform=radar_data.transform, ax=ax, zorder=3)
    show(nummask, transform=radar_data.transform, ax=ax, zorder=4, alpha=.1,
         interpolation='bilinear')
    ax.axis('off')
    ax.set_xlim(left=-5e4)
    ax.set_ylim(top=7.8e6, bottom=6.42e6)
    return ax

