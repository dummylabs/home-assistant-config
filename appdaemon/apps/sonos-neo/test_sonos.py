import appdaemon.plugins.hass.hassapi as hass

class TestSonos(hass.Hass):
    def initialize(self):
        s = self.get_app('neosonos')
        #s.speak('Проверка связи', volume=0.01)
