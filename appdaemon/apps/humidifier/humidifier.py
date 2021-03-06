"""
Manages state of the Xiaomi humidifier, sends an alert when it runs out of water.
"""

import appdaemon.plugins.hass.hassapi as hass
import datetime

class Humidifier(hass.Hass):
    def initialize(self):
        self.messenger = self.get_app('messages')
        self.run_daily(self.switch_on, datetime.time(10, 0, 0))
        self.run_daily(self.switch_off, datetime.time(23, 00, 0))
        self.listen_state(self.state_handler, entity='sensor.humidifier_water_level')
        
    def switch_on(self, kwargs):
        self.call_service('fan/turn_on', entity_id="fan.zhimi_humidifier_ca1")
        self.log('Humidifier switched on')

    def switch_off(self, kwargs):
        self.call_service('fan/turn_off', entity_id="fan.zhimi_humidifier_ca1")
        self.log('Humidifier switched off')


    def state_handler(self, entity, attribute, old, new, kwargs):
        try:
            level = int(new)
        except:
            return
        if not(level % 5) and level<31:
            self.messenger.bell(f'Низкий уровень воды в увлажнителе: {level}')
