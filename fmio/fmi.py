# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from j24 import running_py3

import pandas as pd
if running_py3():
    from urllib.parse import urlretrieve, urlencode
    import urllib.parse as urlparse
else:
    from urllib import urlretrieve, urlencode
    import urlparse
from lxml import etree
from owslib.wfs import WebFeatureService
from os import path, environ
from fmio import USER_DIR, DATA_DIR
import pytz


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FNAME_TIME_FORMAT = '%Y%m%d_%H%M'
FNAME_FORMAT = FNAME_TIME_FORMAT + '.tif'
KEY_FILE_PATH = path.join(USER_DIR, 'api.key')


def read_key(keyfilepath=KEY_FILE_PATH):
    if "FMI_API_KEY" in environ:
        return environ['FMI_API_KEY']
    with open(keyfilepath, 'r') as keyfile:
        return keyfile.readline().splitlines()[0]


def gen_url(timestamp=None):
    kws = dict()
    if timestamp is not None:
        kws['starttime'] = timestamp
        kws['endtime'] = timestamp
    urls = available_maps(**kws)
    t = urls.index.max()
    # Should we also return t?
    return urls[t]


def available_maps(storedQueryID='fmi::radar::composite::rr',
                   resolution_scaling=1, **kws):
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
    s = s.apply(scale_url_width_height, factor=resolution_scaling)
    return s.sort_index()


def download_maps(urls):
    """
    Download rainmaps if they don't exist already. Mainly for testing purposes.

    urls: Series

    Returns paths of the downloaded files.
    """
    save_paths = urls.copy()
    save_dir = path.join(DATA_DIR, 'tmp')
    for t, url in urls.iteritems():
        filename = t.strftime(FNAME_FORMAT)
        filepath = path.join(save_dir, filename)
        if not path.isfile(filepath):
            urlretrieve(url, filename=filepath)
        save_paths.loc[t] = filepath
    return save_paths


def extract_url_params(url):
    parsed = urlparse.urlparse(url)
    params = urlparse.parse_qs(parsed.query)
    for key in params.iterkeys():
        params[key] = params[key][0]
    return params


def replace_url_params(url, update_dict):
    params = extract_url_params(url)
    params.update(update_dict)
    url_parts = list(urlparse.urlparse(url))
    url_parts[4] = urlencode(params)
    return urlparse.urlunparse(url_parts)


def scale_url_width_height(url, factor=1):
    params = extract_url_params(url)
    for key in ('height', 'width'):
        params[key] = int(int(params[key])*factor)
    return replace_url_params(url, params)

