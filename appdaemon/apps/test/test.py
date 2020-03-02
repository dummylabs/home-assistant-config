import appdaemon.plugins.hass.hassapi as hass
import datetime

sensor_id = 'sensor.test_run_once'

class TestApp(hass.Hass):
    def initialize(self):
        pass
        #self.call_service('tts/yandextts_say', entity_id='media_player.kitchen', message='Проверка связи')


