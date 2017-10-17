# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from lxml import etree
from owslib.wfs import WebFeatureService
from fmio import fmi

key = fmi.read_key()
url = 'http://data.fmi.fi/fmi-apikey/{}/wfs'.format(key)

wfs = WebFeatureService(url=url, version='2.0.0')
params = dict(starttime='2017-10-17T07:00:00Z', endtime='2017-10-17T07:30:00Z')
response = wfs.getfeature(storedQueryID='fmi::radar::composite::rr', storedQueryParams=params)
root = etree.fromstring(response.read())
result_query = 'wfs:member/omso:GridSeriesObservation'
file_subquery = 'om:result/gmlcov:RectifiedGridCoverage/gml:rangeSet/gml:File/gml:fileReference'
time_subquery = 'om:resultTime/gml:TimeInstant/gml:timePosition'

d = dict()
for result in root.findall(result_query, root.nsmap):
    t = result.find(time_subquery, root.nsmap).text
    f = result.find(file_subquery, root.nsmap).text
    d[t] = f

