# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from fmio import fmi

t_range = dict(starttime='2017-10-11T07:00:00Z', endtime='2017-10-11T07:30:00Z')

urls = fmi.available_maps(**t_range)
url = fmi.gen_url(timestamp='2017-10-17T07:00:00Z')

dl = urls.tail(2)

paths = fmi.download_maps(dl)
