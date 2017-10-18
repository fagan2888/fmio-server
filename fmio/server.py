import cStringIO
import json
from os import path

import pyproj
import rasterio
from flask import Flask, send_from_directory, send_file, url_for

from dataminer import DataMiner
from fmio import DATA_DIR, FI_RR_FIG_FILEPATH
from fmio import fmi

miner = DataMiner(
    path.join(DATA_DIR, "tmp1"),
    path.join(DATA_DIR, "tmp2"),
    interval_mins=5
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


@app.route("/rains/<lon>/<lat>")
def rains(lon, lat):
    p1 = pyproj.Proj(init='epsg:4326')
    p2 = pyproj.Proj(init='epsg:3067')
    xy = pyproj.transform(p1, p2, lon, lat)
    ret = []
    with miner.temp_swap_lock:
        temp = miner.current_temp()
        for filename in temp.filenames():
            with rasterio.open(temp.path(filename)) as data:
                value = list(data.sample([xy]))[0][0]
                print(xy)
                print(data.sample([xy]))
                print(list(data.sample([xy])))
                ret.append({"time": str(fmi.string_todatetime(filename)), "rain": int(value)})
    return json.dumps(ret)


@app.route("/file")
def file1():
    with miner.temp_swap_lock:
        # return send_from_directory(miner.tempdir, miner.filenames()[0])
        with open(miner.current_temp().filepaths()[0]) as f:
            return send_file(cStringIO.StringIO(f.read()), mimetype="image/png")


@app.route("/png")
def png():
    return send_from_directory(FI_RR_FIG_FILEPATH.format(timestamp=''))
