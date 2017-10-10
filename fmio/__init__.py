#!/usr/bin/env python -p
# coding: utf-8
from os import path
from j24 import home
from fmio import radar

NAME = 'fmio'
CONFIG_DIR = path.join(home(), '.'+NAME)

if __name__ == '__main__':
    radar.main()