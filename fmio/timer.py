import datetime
import time
from threading import Thread


class TimedTask(Thread):
    def __init__(self, interval_mins=5):
        Thread.__init__(self)
        self.daemon = False
        self.interval_mins = interval_mins
        dtime = datetime.datetime.utcnow()
        dtime = dtime.replace(minute=(dtime.minute // self.interval_mins) * self.interval_mins)
        self.dtime = dtime

    def run(self):
        while True:
            if self.dtime < datetime.datetime.utcnow():
                while self.dtime < datetime.datetime.utcnow():
                    self.dtime += datetime.timedelta(minutes=self.interval_mins)
                self.timed_task()
            time.sleep(1)

    def timed_task(self):
        raise NotImplementedError("Please implement this method in inheriting class")
