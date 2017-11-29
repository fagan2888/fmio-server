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

from fmio.tasks import make_forecast
from fmio.dataminer import DataMiner
from fmio import DATA_DIR
from fmio import fmi
from fmio import raster
from j24.selleri import make_celery
import datetime
import pytz
import time
from redis import StrictRedis
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

conn = StrictRedis()
miner = DataMiner(
    path.join(DATA_DIR, "tmp1"),
    path.join(DATA_DIR, "tmp2"),
    path.join(DATA_DIR, "tmp3"),
    path.join(DATA_DIR, "tmp4"),
)

print("Starting up server.")
app = Flask(__name__)
app.config.update(broker_url='redis://localhost:6379',
                  result_backend='redis://localhost:6379')
cel = make_celery(app)


example_mode = 'FMI_EXAMPLE' in environ
if example_mode:
    print("Running in example mode")


@cel.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls update forecast periodically
    sender.add_periodic_task(30.0, update_forecast.s(), name='forecast schedule')


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
    with conn.lock('temp_swap'):
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
    with conn.lock('gif_swap'):
        with open(miner.gif_storage.path("forecast.gif")) as f:
            sent_gif = cStringIO.StringIO(f.read())
    return send_file(sent_gif, mimetype="image/gif")


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@cel.task
def update_forecast():
    logger.info('Trying to retrieve lock.')
    with conn.lock(miner.id, timeout=300*10):
        print("Checking if maps need updating.")
        urls = fmi.available_maps(resolution_scaling=0.7).tail(2)
        current_dates = urls.index
        print("Previous dates:", miner.previous_dates)
        print("Current dates:", current_dates)
        if len(current_dates) == len(miner.previous_dates) and all(current_dates == miner.previous_dates):
            print("No new maps, not updating.")
            return 0 # do nothing
        miner.previous_dates = current_dates
        print("New maps found, generating forecasts.")
        fcast, meta = make_forecast(urls)
        print("Saving generated forecasts.")
        png_paths = miner.save_frames(fcast, meta)
        miner.save_gif(png_paths)
        miner.swap_temps()
        print("Successfully updated maps.")
    return 1 # updated