import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
import globals

class DND(hass.Hass):
    def initialize(self):
        #self.handle = self.run_in(self.my_callback, 5)
        self.listen_state(self.on_masha_door_changed, "binary_sensor.door_masha")
        #self.handle = self.run_hourly(self.my_callback, None)
        self.run_every(self.my_callback, globals.now(), 5*60)

    def my_callback(self, kwargs):
        now = datetime.now().hour
        masha_door = self.get_state("binary_sensor.door_masha")
        if (now >= 22 or now < 8):
            self.turn_on("input_boolean.mode_do_not_disturb")
        elif masha_door == "on":
            self.turn_off("input_boolean.mode_do_not_disturb")
            
    def on_masha_door_changed(self, entity, attribute, old, new, kwargs):
        if new == "off":
            self.turn_on("input_boolean.mode_do_not_disturb")
        else:
            self.turn_off("input_boolean.mode_do_not_disturb")

    def is_set(self):
        return self.get_state('input_boolean.mode_do_not_disturb') == 'on'
            
