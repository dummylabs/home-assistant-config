import appdaemon.plugins.hass.hassapi as hass
import requests
import globals

class HealthChecksIO(hass.Hass):
    def initialize(self):
        self.url = self.args['url']
        self.run_every(self.my_check, globals.now(), 3 *60)
    def my_check(self, kwargs):
        requests.get(self.url, timeout=5)