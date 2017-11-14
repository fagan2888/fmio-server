# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

#import threading
from redis_lock import Lock
from redis import StrictRedis
from os import path, remove, listdir, makedirs
import errno

conn = StrictRedis()

class Storage:
    def __init__(self, tempdir):
        self.tempdir = tempdir
        #self.lock = threading.RLock()
        with Lock(conn, self.tempdir):
            try:
                makedirs(self.tempdir)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
        self.remove_all_files()

    def remove_all_files(self):
        with Lock(conn, self.tempdir):
            for filename in listdir(self.tempdir):
                remove(path.join(self.tempdir, filename))

    def filenames(self):
        """Returns names of the stored files sorted as newest to oldest"""
        with Lock(conn, self.tempdir):
            filenames = listdir(self.tempdir)
        filenames.sort()
        return filenames

    def filepaths(self):
        return map(lambda x: path.join(self.tempdir, x), self.filenames())

    def path(self, filename=""):
        return path.join(self.tempdir, filename)
