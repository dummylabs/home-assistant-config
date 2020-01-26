import appdaemon.plugins.hass.hassapi as hass
import errors
import os
import datetime

class TestApp(hass.Hass):
  def initialize(self):
    msg = self.get_app('messages')
    #msg.message('Проверка связи', category='notify_person_tracking')
    s = self.get_state('binary_sensor.entrance', attribute = 'last_changed')
    self.log(s)
    t = datetime.datetime.fromisoformat(s)
    t2 = t - datetime.timedelta(hours = 1)
    self.log(t2.isoformat())
    #self.set_state('binary_sensor.entrance', attributes={'last_changed':t2.isoformat()})

  def input_handler(self, entity, attribute, old, new, kwargs):
    self.log(entity)
