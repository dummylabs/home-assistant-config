import appdaemon.plugins.hass.hassapi as hass
import errors

class CoffeeMaker(hass.Hass):
    def initialize(self):
        self.listen_state(self.state_handler, 'binary_sensor.coffee_maker')
        self.tts = self.get_app('tts')
        self.start = None

    def state_handler(self, entity, attribute, old, new, kwargs):
        if old == 'off' and new == 'on':
            self.start = now = self.datetime()
        if old == 'on' and new == 'off' and self.start:
            duration = (self.datetime()-self.start).total_seconds()
            self.log('Coffe Maker has been working for {} seconds'.format(duration))
            if duration > 10 and duration < 100:
                self.tts.speak('Возможно вы забыли добавить воду в кофеварку', volume=0.3, opener='notify1.mp3')
            else:
                self.tts.speak('Кофе готов.', volume=0.3, opener='notify1.mp3')
            
            
