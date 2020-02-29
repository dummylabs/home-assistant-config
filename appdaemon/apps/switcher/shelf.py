import shelve
import os, glob
import datetime
from threading import Lock

import appdaemon.plugins.hass.hassapi as hass

class Shelf(hass.Hass):
    def initialize(self):
        self.filename = self.app_dir+'/shelf.db'
        self.log(f'Shelf DB initialized: {self.filename}')

    def get_value(self, what, default=None):
        mutex = Lock()
        mutex.acquire()
        value = default
        try:
            with shelve.open(self.filename, 'c') as shelf:
                if what in shelf:
                    value = shelf[what]
        except Exception as e:
            self.log(f'Exception occurred "{e}"', level = "ERROR")
        mutex.release()
        return value

    def set_value(self, name, val):
        mutex = Lock()
        mutex.acquire()
        try:
            with shelve.open(self.filename, 'c') as shelf:
                shelf[name] = val
        except Exception as e:
            self.log(f'Exception occurred "{e}"', level = "ERROR")
        mutex.release()
