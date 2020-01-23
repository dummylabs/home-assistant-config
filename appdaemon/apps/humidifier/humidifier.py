import appdaemon.plugins.hass.hassapi as hass
import datetime

# 
class Humidifier(hass.Hass):
    def initialize(self):
        self.messenger = self.get_app('messages')
        self.run_once(self.switch_on, datetime.time(10, 0, 0))
        self.run_once(self.switch_off, datetime.time(23, 00, 0))
        self.listen_state(self.state_handler, entity='sensor.humidifier_water_level')
        
    def switch_on(self, kwargs):
        self.call_service('fan/turn_on', entity_id="fan.zhimi_humidifier_ca1")
        self.log('Humidifier switched on')

    def switch_off(self, kwargs):
        self.call_service('fan/turn_off', entity_id="fan.zhimi_humidifier_ca1")
        self.log('Humidifier switched off')

    def check_level(self, kwargs):
        level = int(self.get_state('sensor.humidifier_water_level'))
        if level < 40:
           self.log(f'Humidifier level is low ({level})')
           self.messenger.alert(f'Низкий уровень воды в увлажнителе: {level}')

    def state_handler(self, entity, attribute, old, new, kwargs):
        level = int(new)
        self.log(f'Humidifier level: ({level})')
        if not(level % 5) and level<31:
            self.messenger.alert(f'Низкий уровень воды в увлажнителе: {level}')
