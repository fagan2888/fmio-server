# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from j24 import running_py3

import rasterio
import numpy as np
import pandas as pd
if running_py3():
    from urllib.parse import urlencode, urlretrieve
else:
    from urllib import urlencode, urlretrieve
from lxml import etree
from owslib.wfs import WebFeatureService
from rasterio.plot import show
from os import path, environ
from fmio import USER_DIR, DATA_DIR
import datetime
import time
import pytz


DBZ_NODATA = 255
RR_NODATA = 65535
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FNAME_FORMAT = '%Y%m%d_%H%M.tif'
KEY_FILE_PATH = path.join(USER_DIR, 'api.key')


def raw2rr(raw):
    return raw*0.01


def read_key(keyfilepath=KEY_FILE_PATH):
    if "FMI_API_KEY" in environ:
        return environ['FMI_API_KEY']
    with open(keyfilepath, 'r') as keyfile:
        return keyfile.readline().splitlines()[0]


def to_datetime(ttime):
    dtime = datetime.datetime.fromtimestamp(ttime)
    return dtime


def to_time(dtime):
    ttime = (dtime - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return ttime


def gen_url(timestamp=None):
    kws = dict()
    if timestamp is not None:
        kws['starttime'] = timestamp
        kws['endtime'] = timestamp
    urls = available_maps(**kws)
    t = urls.index.max()
    # Should we also return t?
    return urls[t]


def available_maps(storedQueryID='fmi::radar::composite::rr', **kws):
    """
    If given, start and end times are passed as query parameters, e.g.:
    starttime='2017-10-17T07:00:00Z', endtime='2017-10-17T07:30:00Z'

    output: Series of WMS links with timezone aware index in UTC time
    """
    key = read_key()
    url_wfs = 'http://data.fmi.fi/fmi-apikey/{}/wfs'.format(key)
    wfs = WebFeatureService(url=url_wfs, version='2.0.0')
    response = wfs.getfeature(storedQueryID=storedQueryID, storedQueryParams=kws)
    root = etree.fromstring(response.read().encode('utf8'))
    result_query = 'wfs:member/omso:GridSeriesObservation'
    file_subquery = 'om:result/gmlcov:RectifiedGridCoverage/gml:rangeSet/gml:File/gml:fileReference'
    time_subquery = 'om:resultTime/gml:TimeInstant/gml:timePosition'
    d = dict()
    for result in root.findall(result_query, root.nsmap):
        t = result.find(time_subquery, root.nsmap).text
        f = result.find(file_subquery, root.nsmap).text
        d[t] = f
    s = pd.Series(d)
    s.index = pd.DatetimeIndex(s.index, tz=pytz.utc)
    return s.sort_index()


def download_maps(maps):
    """maps: Series"""
    save_paths = maps.copy()
    save_dir = path.join(DATA_DIR, 'tmp')
    for t, url in maps.iteritems():
        filename = t.strftime(FNAME_FORMAT)
        filepath = path.join(save_dir, filename)
        urlretrieve(url, filename=filepath)
        save_paths.loc[t] = filepath
    return save_paths


def plot_radar_map(radar_data, border=None, cities=None, ax=None, crop='fi'):
    dat = radar_data.read(1)
    mask = dat==RR_NODATA
    d = dat.copy()*0.01
    d[mask] = 0
    datm = np.ma.MaskedArray(data=d, mask=d==0)
    nummask = np.ma.MaskedArray(data=dat, mask=~mask)
    ax = show(datm, transform=radar_data.transform, ax=ax, zorder=3)
    show(nummask, transform=radar_data.transform, ax=ax, zorder=4, alpha=.1,
         interpolation='bilinear')
    if border is not None:
        border.to_crs(radar_data.read_crs().data).plot(zorder=0, color='gray',
                                                       ax=ax)
    if cities is not None:
        cities.to_crs(radar_data.read_crs().data).plot(zorder=5, color='black',
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

