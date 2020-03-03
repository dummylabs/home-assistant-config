"""
The app to count errors occurred in an app and send a message
when the number of errors happened in the row exceeds the treshold
"""
import globals
import appdaemon.plugins.hass.hassapi as hass
from messages import Messenger
import sys

class ErrorCounter(hass.Hass):
    def initialize(self):
        self.path = self.args['shelf_path']
        self.messenger = self.get_app('messages')
        self.treshold = self.args['treshold']
        self.db = self.get_app('shelf')

    def _get_id(self, err_id):
        eid = err_id or sys._getframe(2).f_globals['__file__']
        return f"error${eid}"

    def add(self, err_id=None):
        err_id = self._get_id(err_id)
        err_count = self.db.get_value(err_id, 0)
        if err_count > self.treshold:
            msg = 'Too many errors ({}) for {}'.format(err_count, err_id)
            self.messenger.alert(msg)
        self.db.set_value(err_id, err_count + 1)

    def reset(self, err_id=None):
        err_id = self._get_id(err_id)
        self.db.set_value(err_id, 0)
