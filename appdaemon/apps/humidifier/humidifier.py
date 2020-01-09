import appdaemon.plugins.hass.hassapi as hass
import datetime

class Humidifier(hass.Hass):
    def initialize(self):
        self.run_once(self.switch_on, datetime.time(10, 0, 0))
        self.run_once(self.switch_off, datetime.time(23, 00, 0))

    def switch_on(self, kwargs):
        self.call_service('fan/turn_on', entity_id="fan.zhimi_humidifier_ca1")
        self.log('Humidifier switched on')

    def switch_off(self, kwargs):
        self.call_service('fan/turn_off', entity_id="fan.zhimi_humidifier_ca1")
        self.log('Humidifier switched off')
