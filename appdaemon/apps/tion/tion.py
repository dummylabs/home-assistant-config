import appdaemon.plugins.hass.hassapi as hass
import errors
import os
import datetime

class Tion(hass.Hass):
  def initialize(self):
     self.listen_event(self.change_speed, 'xiaomi_aqara.click', entity_id = 'binary_sensor.switch_tion')
     self.listen_event(self.on_coffee, "coffee_maker.start")

  def on_coffee(self, event_name, data, kwargs):
      self.set_speed(4)

  def set_speed(self, speed):
     self.log(f'set speed to {speed}')
     self.call_service("climate/set_fan_mode", entity_id="climate.tion_breezer_3s_1", fan_mode=f"{speed}")
     self.call_service("tts/yandextts_say", entity_id="media_player.home_hub_max", message=f'скорость {speed}')

  def change_speed(self, event_name, data, kwargs):
     self.log(f'{event_name} {data}')
     click_type = data['click_type']
     current_speed = int(self.get_state('climate.tion_breezer_3s_1', 'speed'))
     speed = None
     if click_type == 'single':
         if current_speed == 1:
             speed = 4
         else:
             speed = 1
     elif click_type == 'double':
             speed = 6
     if speed:
         self.set_speed(speed)

