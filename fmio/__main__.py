#!/usr/bin/env python -p
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import time
import numpy as np
import geopandas as gpd
import rasterio
import tempfile
import matplotlib.pyplot as plt
from os import path
from rasterio.plot import show
from urllib.request import urlretrieve
from j24.server import GracefulKiller
from fmio import USER_DIR

def generate_url(keyfilepath):
    with open(keyfilepath, 'r') as keyfile:
        key = keyfile.readline().splitlines()[0]
    radurl_base = 'http://wms.fmi.fi/fmi-apikey/{}/geoserver/Radar/ows?service=WMS&request=GetMap&format=image/geotiff&bbox=-118331.366,6335621.167,875567.732,7907751.537&width=1700&height=2500&srs=EPSG:3067&layers=Radar:suomi_dbz_eureffin'
    return radurl_base.format(key)

def read_basemap(shapefilepath, country_key='ADMIN'):
    world = gpd.read_file(shapefilepath)
    return world[world[country_key]=='Finland']

def plot_radar_map(radar_data, basemap, cities=None):
    dat = radar_data.read(1)
    mask = dat==252
    d = dat.copy()
    d[mask] = 0
    datm = np.ma.MaskedArray(data=d, mask=d==0)
    nummask = np.ma.MaskedArray(data=dat, mask=~mask)
    ax = basemap.to_crs(radar_data.read_crs().data).plot(zorder=0, color='gray')
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

def update_radar_data(output_filepath, debug=False):
    data_path = path.join(path.dirname(__file__), 'data')
    config_dir = USER_DIR
    keyfilepath = path.join(config_dir, 'api.key')
    radurl = generate_url(keyfilepath)
    with tempfile.TemporaryDirectory() as tmp_path:
        radarfilepath = path.join(tmp_path, 'Radar-suomi_dbz_eureffin.tif')
        urlretrieve(radurl, filename=radarfilepath)
        country_filepath = path.join(data_path, 'ne_10m_admin_0_countries.shp')
        cities_filepath = path.join(data_path, 'ne_10m_populated_places.shp')
        basemap = read_basemap(country_filepath, country_key='ADMIN')
        cities = read_basemap(cities_filepath, country_key='ADM0NAME')
        with rasterio.open(radarfilepath) as radar_data:
            ax = plot_radar_map(radar_data, basemap, cities=cities)
        fig = ax.get_figure()
        fig.savefig(output_filepath)
    print('Updated {}.'.format(output_filepath))
    if not debug:
        plt.close(fig)

def main():
    debug = True
    if debug:
        plt.ion()
        sleep_time = 5 # seconds
    else:
        plt.ioff()
        sleep_time = 5*60
    killer = GracefulKiller()
    while True:
        time.sleep(sleep_time)
        update_radar_data('test.png', debug=debug)
        if killer.kill_now:
            break

if __name__ == '__main__':
    main()
