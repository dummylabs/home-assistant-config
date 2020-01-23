#encoding utf-8
import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime

#binary_sensor.switch_158d0001a66c1b
class SayWeather(hass.Hass):
    def initialize(self):
        now = self.datetime()
        self.handle = None
        self.messenger = self.get_app('messages')

        #self.handle = self.run_every(self.my_callback, now, 15*60)
        #self.handle = self.run_in(self.my_callback, 5)
        #self.handle = self.run_hourly(self.my_callback, None)
        #self.tts = self.get_app('tts')
        self.tts = self.get_app('neosonos')
        self.listen_event(self.say_weather, 'xiaomi_aqara.click', entity_id = 'binary_sensor.switch_announcer', click_type = "single")
        self.listen_state(self.say_entrance_opened, 'binary_sensor.entrance')

    def say_weather(self, event_name, data, kwargs):
        self.log('Click type=' + data["click_type"])
        actual_temp = self.get_state("sensor.yandex_weather_temperature")
        apparent_temp = self.get_state("sensor.yandex_weather_apparent_temperature")
        nowcast = self.get_state("sensor.yandex_weather_nowcast_alert")
        if actual_temp == apparent_temp:
            text = u"Сейчас на улице {}°C - - - - - - - - - - - - ".format(actual_temp)
        else:
            text = u"Сейчас на улице {}°C, - ощущается как {}  - - - - - - - - - - - - ".format(actual_temp, apparent_temp)
        text += nowcast
        #self.call_service("script/sonos_say", speed = 3, message = text, sonos_entity = "media_player.kitchen", volume = 0.5, cache = "false")
        self.tts.speak(text)
        self.log('Text spoken')
 
    def delayed_announce(self, kwargs):
        message = 'Входная дверь открыта!'
        if self.get_state('input_select.dima_status_dropdown') == 'just arrived':
            message = 'Ваш папа пришёл!'
        self.tts.speak(message)
        for person in ['device_tracker.phone_dima', 'device_tracker.phone_vika']:
            if self.get_state(person) == 'home':
                return
        #self.messenger.message(message)
        #self.tts.speak('Входная дверь открыта!')

    def say_entrance_opened(self, entity, attribute, old, new, kwargs):

        if self.handle:
            self.cancel_timer(self.handle) 
        if old == 'off' and new == 'on':
            self.handle = self.run_in(self.delayed_announce, 2)
