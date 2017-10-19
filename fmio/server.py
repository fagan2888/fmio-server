import cStringIO
import json
from os import path

import pyproj
import rasterio
from flask import Flask, send_from_directory, send_file, url_for

from dataminer import DataMiner
from fmio import DATA_DIR, FI_RR_FIG_FILEPATH
from fmio import fmi
import datetime
import pytz

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
    p1 = pyproj.Proj(init='epsg:4326')
    p2 = pyproj.Proj(init='epsg:3067')
    xy = pyproj.transform(p1, p2, lon, lat)
    ret = []
    with miner.temp_swap_lock:
        temp = miner.current_temp()
        print("Filenames:", temp.filenames())
        for filename in temp.filenames():
            if filename.endswith(".tif"):
                with rasterio.open(temp.path(filename)) as data:
                    value = list(data.sample([xy]))[0][0]
                    dtime = datetime.datetime.strptime(filename, fmi.FNAME_FORMAT).replace(tzinfo=pytz.UTC)
                    # if dtime > datetime.datetime.utcnow(): # Only show forecasts newer than "now"
                    stime = dtime.strftime(fmi.TIME_FORMAT)
                    ret.append({"time": stime, "rain_intensity": float(value), "rain_intensity_mm_h": float(value)*0.01})
    return json.dumps({"time_format": fmi.TIME_FORMAT, "timezone": str(pytz.UTC), "forecasts": ret})


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
