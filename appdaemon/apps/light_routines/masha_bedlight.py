import appdaemon.plugins.hass.hassapi as hass
import datetime

class MashaBedlight(hass.Hass):
    def initialize(self):
        self.entity_id = 'light.bedlight_masha' 
        self.run_daily(self.switch_on, "21:50:00")
        self.run_daily(self.switch_off, "sunrise + 00:20:00")

    def switch_on(self, kwargs):
        self.call_service("light/turn_on", entity_id=self.entity_id)
    def switch_off(self, kwargs):
        self.call_service("light/turn_off", entity_id=self.entity_id)


