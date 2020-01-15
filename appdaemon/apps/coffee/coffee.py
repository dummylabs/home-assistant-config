import appdaemon.plugins.hass.hassapi as hass
import errors

treshold = 40

class CoffeeMaker(hass.Hass):
    def initialize(self):
        self.listen_state(self.state_handler, 'sensor.switch_coffee_maker_power')
        self.tts = self.get_app('tts')
        self.start = None

    def state_handler(self, entity, attribute, old, new, kwargs):
        old = float(old)
        new = float(new)
        if old < treshold and new >= treshold:
            self.log('Counter started')
            self.start = now = self.datetime()
        if old >= treshold and new < treshold and self.start:
            duration = (self.datetime()-self.start).total_seconds()
            self.log('Coffe Maker has been working for {} seconds'.format(duration))
            if duration > 10:
                if duration < 100:
                    self.tts.speak('Возможно вы забыли добавить воду в кофеварку', volume=0.3, opener='notify1.mp3')
                else:
                    self.tts.speak('Кофе готов.', volume=0.3, opener='notify1.mp3')
