import appdaemon.plugins.hass.hassapi as hass
import errors
import os

class TestApp(hass.Hass):
  def initialize(self):
    self.listen_state(self.input_handler, "person") 

  def input_handler(self, entity, attribute, old, new, kwargs):
    self.log(entity)
