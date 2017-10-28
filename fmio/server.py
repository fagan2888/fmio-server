# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import matplotlib
matplotlib.use("agg")  # avoid using tkinter

import cStringIO
import json
from os import path, environ

import rasterio
from flask import Flask, send_from_directory, send_file, url_for

from fmio.dataminer import DataMiner
from fmio import DATA_DIR, FI_RR_FIG_FILEPATH
from fmio import fmi
from fmio import raster
import datetime
import pytz
import time

print("Starting up server.")

example_mode = 'FMI_EXAMPLE' in environ
if example_mode:
    print("Running in example mode")

miner = DataMiner(
    path.join(DATA_DIR, "tmp1"),
    path.join(DATA_DIR, "tmp2"),
    path.join(DATA_DIR, "tmp3"),
    path.join(DATA_DIR, "tmp4"),
    interval_mins=1
)
if not example_mode:
    miner.start()

app = Flask(__name__)


def generate_example_data():
    forecasts = []
    interval = 1
    ttime = time.time()
    timestamp = datetime.datetime.utcnow()
    timestamp = timestamp.replace(minute=(timestamp.minute // interval) * interval, second=0)
    rates = [0.1,0.0,0.0,0.0,0.2,0.1,
             0.2,0.4,0.6,0.6,0.6,0.4,0.2]
    for i in range(len(rates)):
        mm_h = rates[int((i+ttime//(60*interval)) % len(rates))]
        dtime = timestamp + datetime.timedelta(minutes=i*interval)
        forecasts.append({
            "time": dtime.strftime(fmi.TIME_FORMAT),
            "rain_intensity": mm_h
        })
    return json.dumps({
        "time_format": fmi.TIME_FORMAT,
        "timezone": str(pytz.UTC),
        "forecasts": forecasts,
        "accumulation": raster.accumulation(map(lambda x: x['rain_intensity'], forecasts), 1),
    })


@app.route("/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        url = url_for(rule.endpoint, **{x: "-{}-".format(x) for x in rule.arguments})
        links.append("{}".format((url, rule.endpoint)))
    return "{}".format("<br/>".join(links))


@app.route("/forecast/<lon>/<lat>")
def forecast(lon, lat):
    if example_mode:
        return generate_example_data()
    x, y = raster.lonlat_to_xy(lon, lat)
    forecasts = []
    with miner.temp_swap_lock:
        temp = miner.current_temp()
        for filename in temp.filenames():
            with rasterio.open(temp.path(filename)) as data:
                mm_h = raster.rr_at_coords(data, x, y)
                timestamp = raster.filename_to_datestring(filename)
                forecasts.append({"time": timestamp, "rain_intensity": mm_h})
    return json.dumps({
        "time_format": fmi.TIME_FORMAT,
        "timezone": str(pytz.UTC),
        "forecasts": forecasts,
        "accumulation": raster.accumulation(map(lambda x: x['rain_intensity'], forecasts), 5),
    })


@app.route("/rainmap/<rand>/")
@app.route("/rainmap")
@app.route("/rainmap.gif")
def gif(**kwargs):
    if example_mode:
        return send_from_directory(DATA_DIR, "forecast.gif")
    with miner.gif_swap_lock:
        with open(miner.gif_storage.path("forecast.gif")) as f:
            sent_gif = cStringIO.StringIO(f.read())
    return send_file(sent_gif, mimetype="image/gif")


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response
