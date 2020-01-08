import globals
import appdaemon.plugins.hass.hassapi as hass
from messages import Messenger
import sys

class ErrorCounter(hass.Hass):
    def initialize(self):
        self.path = self.args['shelf_path']
        self.messenger = self.get_app('messages')
        self.treshold = self.args['treshold']

    def _get_id(self, err_id):
        return err_id or sys._getframe(2).f_globals['__file__']

    def add(self, err_id=None):
        err_id = self._get_id(err_id)
        err_count = globals.get_value(self.path, err_id, 0)
        if err_count > self.treshold:
            msg = 'Too many errors ({}) for {}'.format(err_count, err_id)
            self.messenger.alert(msg)
        globals.set_value(self.path, err_id, err_count + 1)

    def reset(self, err_id=None):
        err_id = self._get_id(err_id)
        globals.set_value(self.path, err_id, 0)
