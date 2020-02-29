import appdaemon.plugins.hass.hassapi as hass
import errors

treshold = 40

class CoffeeMaker(hass.Hass):
    def initialize(self):
        self.listen_state(self.state_handler, 'sensor.switch_coffee_maker_power')
        self.tts = self.get_app('neosonos')
        self.start_time = None
        self.event_fired = False

    def state_handler(self, entity, attribute, old, new, kwargs):
        if old == 'unavailable' or new == 'unavailable':
            return 
            
        old = float(old)
        new = float(new)
            
        duration = (self.datetime()-self.start_time).total_seconds() if self.start_time else 0

        if old < treshold and new >= treshold:
            self.log('Counter started')
            self.event_fired = False
            self.start_time = now = self.datetime()

        if duration > 10 and not self.event_fired:
            self.fire_event('coffee_maker.start')
            self.event_fired = True

        if old >= treshold and new < treshold and self.start_time:
            #duration = (self.datetime()-self.start_time).total_seconds()
            self.log('Coffe Maker has been working for {} seconds'.format(duration))
            self.start_time = None
            if duration > 10:
                if duration < 100:
                    self.tts.speak('Возможно вы забыли добавить воду в кофеварку', volume=0.3, opener='notify1.mp3')
                else:
                    self.tts.speak('Кофе готов.', volume=0.3, opener='notify1.mp3')
