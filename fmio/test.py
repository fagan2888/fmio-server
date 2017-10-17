# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from fmio import fmi

params = dict(starttime='2017-10-17T07:00:00Z', endtime='2017-10-17T07:30:00Z')

d = fmi.available_maps_between()