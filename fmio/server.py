from flask import Flask, send_from_directory, send_file, url_for
from dataminer import DataMiner
from os import path, environ
from fmio import DATA_DIR
import cStringIO
import threading

key = environ['FMI_API_KEY']
tempdir = path.join(DATA_DIR, "tmp")
miner = DataMiner(key, tempdir, stored_count=3)


def update_forecast(debug=False):
    if debug:
        interval = 5
    else:
        interval = 5*60
    miner.fetch_radar_data()
    # build forecast after fetching the data
    # miner.write_test_png()  # dumping some test file instead
    timer = threading.Timer(interval, update_forecast)
    timer.daemon = True
    timer.start()


# Disabled for now not to eat out resources
# update_forecast()

app = Flask(__name__)

@app.route("/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        url = url_for(rule.endpoint, **{x: "-{}-".format(x) for x in rule.arguments})
        links.append("{}".format((url, rule.endpoint)))
    return "{}".format("<br/>".join(links))

@app.route("/rains/<location>/")
def rains(location):
    return "Not at {}".format(location)

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
    return send_from_directory(DATA_DIR, "test.png")
