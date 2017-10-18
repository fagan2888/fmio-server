import datetime
import time
from threading import Thread


class TimedTask(Thread):
    def __init__(self, interval_mins=5):
        Thread.__init__(self)
        self.daemon = True
        self.interval_mins = interval_mins
        dtime = datetime.datetime.now()
        dtime = dtime.replace(minute=(dtime.minute // self.interval_mins) * self.interval_mins)
        self.dtime = dtime

    def run(self):
        while True:
            if self.dtime < datetime.datetime.now():
                self.timed_task()
                while self.dtime < datetime.datetime.now():
                    self.dtime += datetime.timedelta(minutes=self.interval_mins)
            time.sleep(60)

    def timed_task(self):
        raise NotImplementedError("Please implement this method in inheriting class")
