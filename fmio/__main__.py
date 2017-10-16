#!/usr/bin/env python -p
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from j24 import running_py3

import time
import matplotlib.pyplot as plt
from os import path
if running_py3():
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve
from j24.server import GracefulKiller
from fmio import fmi, FI_RR_FIG_FILEPATH
if running_py3():
    import tempfile
else:
    from backports import tempfile


def update_radar_figure(output_filepath, debug=False):
    radurl = fmi.gen_url()
    with tempfile.TemporaryDirectory() as tmp_path:
        radarfilepath = path.join(tmp_path, 'Radar-suomi_dbz_eureffin.tif')
        urlretrieve(radurl, filename=radarfilepath)
        border = basemap.border()
        cities = basemap.cities()
        ax = fmi.plot_radar_file(radarfilepath, border=border, cities=cities)
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
        fig_path = FI_RR_FIG_FILEPATH.format(timestamp='')
        update_radar_figure(fig_path, debug=debug)
        if killer.kill_now:
            break


if __name__ == '__main__':
    main()
