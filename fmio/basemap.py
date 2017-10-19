# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import geopandas as gpd
from shapely.geometry import Polygon
from os import path
from fmio import DATA_DIR
from fmio.raster import DEFAULT_CORNERS


def read_basemap(shapefilepath, country_key='ADMIN', country='Finland'):
    world = gpd.read_file(shapefilepath)
    return world[world[country_key]==country]


def cities(**kws):
    cities_filepath = path.join(DATA_DIR, 'ne_10m_populated_places.shp')
    return read_basemap(cities_filepath, country_key='ADM0NAME', **kws)


def border(**kws):
    country_filepath = path.join(DATA_DIR, 'ne_10m_admin_0_countries.shp')
    return read_basemap(country_filepath, country_key='ADMIN', **kws)


def box(x0=DEFAULT_CORNERS['x0'], y0=DEFAULT_CORNERS['y0'],
        x1=DEFAULT_CORNERS['x1'], y1=DEFAULT_CORNERS['y1']):
    p = Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    box = gpd.GeoSeries(p)
    box.crs = dict(init='epsg:3067')
    return box


def plot_edge(shape, edgecolor='red', facecolor=(0, 0, 0, 0), **kws):
    return shape.plot(edgecolor=edgecolor, facecolor=facecolor, **kws)

