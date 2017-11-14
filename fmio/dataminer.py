# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

#import threading
from fmio.storage import Storage
from fmio.timer import TimedTask
from fmio.tasks import update_forecast
from redis_lock import Lock
from redis import StrictRedis

conn = StrictRedis()


class DataMiner(TimedTask):
    def __init__(self, tempdir1, tempdir2, image_temp1, image_temp2, interval_mins=5):
        TimedTask.__init__(self, interval_mins=interval_mins)
        self.temps = [Storage(tempdir1), Storage(tempdir2)]
        #self.temp_swap_lock = threading.RLock()
        #self.gif_swap_lock = threading.RLock()
        self.png_storage = Storage(image_temp1)
        self.gif_storage = Storage(image_temp2)
        self.tempidx = 0
        self.previous_dates = []
        self.task_forecast = None

    def swap_temps(self):
        with Lock(conn, 'temp_swap'):
            self.tempidx = (self.tempidx + 1) % len(self.temps)

    def current_temp(self):
        return self.temps[self.tempidx]

    def download_temp(self):
        return self.temps[(self.tempidx + 1) % len(self.temps)]

    def update_maps(self):
        return update_forecast.delay(self)

    def timed_task(self):
        if self.task_forecast is not None:
            print(self.task_forecast.status)
            if self.task_forecast.status == 'STARTED':
                print('Previous forecast not ready yet. Not starting new one.')
                return
        self.task_forecast = self.update_maps()
