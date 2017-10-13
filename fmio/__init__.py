#!/usr/bin/env python -p
# coding: utf-8
from os import path
from j24 import home

NAME = 'fmio'
USER_DIR = path.join(home(), '.'+NAME)
DATA_DIR = path.join(path.dirname(__file__), 'data')
