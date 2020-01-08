import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime

class DND(hass.Hass):
    def initialize(self):
        #self.handle = self.run_in(self.my_callback, 5)
        self.listen_state(self.on_dnd_mode_changed, "input_boolean.mode_do_not_disturb")
        #self.handle = self.run_hourly(self.my_callback, None)
        self.run_every(self.my_callback, self.datetime(), 5*60)

    def my_callback(self, kwargs):
        now = datetime.now().hour
        if now >= 22 or now < 8:
            self.turn_on("input_boolean.mode_do_not_disturb")
        else:
            self.turn_off("input_boolean.mode_do_not_disturb")
            
    def on_dnd_mode_changed(self, entity, attribute, old, new, kwargs):
        pass
