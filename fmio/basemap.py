# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import geopandas as gpd
from os import path
from fmio import DATA_DIR


def read_basemap(shapefilepath, country_key='ADMIN', country='Finland'):
    world = gpd.read_file(shapefilepath)
    return world[world[country_key]==country]


def cities(**kws):
    cities_filepath = path.join(DATA_DIR, 'ne_10m_populated_places.shp')
    return read_basemap(cities_filepath, country_key='ADM0NAME', **kws)


def border(**kws):
    country_filepath = path.join(DATA_DIR, 'ne_10m_admin_0_countries.shp')
    return read_basemap(country_filepath, country_key='ADMIN', **kws)
