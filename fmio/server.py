from flask import Flask, send_from_directory, send_file, url_for
from dataminer import DataMiner
from os import path
from fmio import DATA_DIR, FI_RR_FIG_FILEPATH
import cStringIO
import threading
import time
import pyproj
import json

tempdir = path.join(DATA_DIR, "tmp")
miner = DataMiner(tempdir, stored_count=3)


def update_forecast(debug=False):
    if debug:
        interval = 5
    else:
        interval = 5*60
    timer = threading.Timer(interval, update_forecast)
    timer.daemon = True
    timer.start()
    miner.fetch_radar_data()

if __name__ == '__main__':
    start_time = time.time()
    miner.fetch_radar_data(start_time - 5 * 60)
    miner.fetch_radar_data(start_time)
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
    # fetch pixel value from tif:
    # ret = []
    # with storage.lock:
    #   for filename in storage.filenames():
    #       with rasterio.open(path.join(storage.path, filename)) as data:
    #           value = data.sample([xy])[0]
    #           ret.append({"time": int(filename), value})
    # return json.dumps(ret)
    return "not implemented. Coords: {}".format(xy)

@app.route("/file")
def file1():
    with miner.lock:
        with open(path.join(miner.tempdir, miner.filenames()[0])) as f:
            return send_file(cStringIO.StringIO(f.read()), mimetype="image/png")

@app.route("/file2")
def file2():
    with miner.lock:
        return send_from_directory(miner.tempdir, miner.filenames()[0])

@app.route("/png")
def png():
    return send_from_directory(FI_RR_FIG_FILEPATH.format(timestamp=''))

# app.run()
