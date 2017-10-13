#!/usr/bin/env python -p
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import time
import rasterio
import tempfile
import matplotlib.pyplot as plt
from os import path
from urllib.request import urlretrieve
from j24.server import GracefulKiller
from fmio import USER_DIR, basemap, fmi


def update_radar_data(output_filepath, debug=False):
    config_dir = USER_DIR
    keyfilepath = path.join(config_dir, 'api.key')
    radurl = fmi.gen_url(keyfilepath)
    with tempfile.TemporaryDirectory() as tmp_path:
        radarfilepath = path.join(tmp_path, 'Radar-suomi_dbz_eureffin.tif')
        urlretrieve(radurl, filename=radarfilepath)
        border = basemap.border()
        cities = basemap.cities()
        with rasterio.open(radarfilepath) as radar_data:
            ax = fmi.plot_radar_map(radar_data, border, cities=cities)
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
        update_radar_data('test.png', debug=debug)
        if killer.kill_now:
            break


if __name__ == '__main__':
    main()
