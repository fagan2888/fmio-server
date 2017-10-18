from flask import Flask, send_from_directory, send_file, url_for
from dataminer import DataMiner
from os import path
from fmio import DATA_DIR, FI_RR_FIG_FILEPATH
import cStringIO
import threading
import time
import pyproj
from fmio.storage import Storage
import json
import rasterio

interval = 5*60
tempdir = path.join(DATA_DIR, "tmp")
tempstore = path.join(DATA_DIR, "tmp_store")

miner = DataMiner(tempdir, stored_count=3)
store = Storage(tempstore)


def update_forecast():
    timer = threading.Timer(interval, update_forecast)
    timer.daemon = True
    timer.start()
    miner.fetch_radar_data()


start_time = time.time()
miner.fetch_radar_data(start_time - interval)
update_forecast()

app = Flask(__name__)


@app.route("/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        url = url_for(rule.endpoint, **{x: "-{}-".format(x) for x in rule.arguments})
        links.append("{}".format((url, rule.endpoint)))
    return "{}".format("<br/>".join(links))


@app.route("/rains/<lon>/<lat>")
def rains(lon, lat):
    p1 = pyproj.Proj(init='epsg:4326')
    p2 = pyproj.Proj(init='epsg:3067')
    xy = pyproj.transform(p1, p2, lon, lat)
    ret = []
    with miner.lock:
        for filename in miner.filenames():
            with rasterio.open(path.join(miner.tempdir, filename)) as data:
                value = list(data.sample([xy]))[0][0]
                print(xy)
                print(data.sample([xy]))
                print(list(data.sample([xy])))
                ret.append({"time": int(filename), "rain": int(value)})
    return json.dumps(ret)


@app.route("/file")
def file1():
    with miner.lock:
        with open(miner.filepaths()[0]) as f:
            return send_file(cStringIO.StringIO(f.read()), mimetype="image/png")


@app.route("/file2")
def file2():
    with miner.lock:
        return send_from_directory(miner.tempdir, miner.filenames()[0])


@app.route("/png")
def png():
    return send_from_directory(FI_RR_FIG_FILEPATH.format(timestamp=''))
