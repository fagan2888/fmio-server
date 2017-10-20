# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import cStringIO
import json
from os import path

import pyproj
import rasterio
from flask import Flask, send_from_directory, send_file, url_for

from fmio.dataminer import DataMiner
from fmio import DATA_DIR, FI_RR_FIG_FILEPATH
from fmio import fmi
from fmio import raster
import datetime
import pytz

print("Starting up server.")

miner = DataMiner(
    path.join(DATA_DIR, "tmp1"),
    path.join(DATA_DIR, "tmp2"),
    interval_mins=1
)
miner.start()

app = Flask(__name__)


@app.route("/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        url = url_for(rule.endpoint, **{x: "-{}-".format(x) for x in rule.arguments})
        links.append("{}".format((url, rule.endpoint)))
    return "{}".format("<br/>".join(links))


@app.route("/forecast/<lon>/<lat>")
def forecast(lon, lat):
    x, y = raster.lonlat_to_xy(lon, lat)
    forecasts = []
    with miner.temp_swap_lock:
        temp = miner.current_temp()
        for filename in temp.filenames():
            with rasterio.open(temp.path(filename)) as data:
                mm_h = raster.rr_at_coords(data, x, y)
                timestamp = raster.filename_to_datestring(filename)
                forecasts.append({"time": timestamp, "rain_intensity": mm_h})
    return json.dumps({"time_format": fmi.TIME_FORMAT, "timezone": str(pytz.UTC), "forecasts": forecasts})


@app.route("/rainmap")
def rainmap():
    with miner.temp_swap_lock:
        temp = miner.current_temp()
        for filename in temp.filenames():
            if filename.endswith(".png"):
                # return send_from_directory(miner.tempdir, miner.filenames()[0])
                with open(temp.path(filename)) as f:
                    return send_file(cStringIO.StringIO(f.read()), mimetype="image/png")
    return "No rainmaps stored"


@app.route("/png")
def png():
    return send_from_directory(FI_RR_FIG_FILEPATH.format(timestamp=''))
