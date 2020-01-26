import appdaemon.plugins.hass.hassapi as hass
import datetime
import globals

TRIGGER1 = "input_boolean.mode_take_pill"
TRIGGER2 = "input_boolean.mode_take_vitamin"
BUTTON = "button.pill_reminder"
SILENT = False

#states.input_boolean.mode_pill_reminder.last_updated

class PillReminder(hass.Hass):
    def initialize(self):
        self.repeat_every = self.args['repeat_every']
        self.run_vitamin_after = self.args['run_vitamin_afer']
        self.tts = self.get_app('neosonos')
        self.messenger = self.get_app('messages')
        #self.listen_state(self.on_coffee, 'binary_sensor.coffee_maker')
        self.listen_event(self.disarm, 'xiaomi_aqara.click', entity_id = 'binary_sensor.switch_pill_confirmed', click_type = "single")
        self.pill_handle = None
        self.vitamin_handle = None
        self.run_once(self.arm, datetime.time(7, 25, 0))
        self.listen_event(self.on_test, "TEST")
        self.listen_event(self.on_test2, "TEST2")
        self.listen_event(self.on_test, "coffee_maker.start")

    def speak(self, text):                       
        if not SILENT:
            self.tts.speak(text,volume=0.3)

    def on_coffee_started(self):
        if not self.pill_handle and self.is_armed(TRIGGER1):
            self.log('Coffee is brewing, start pills reminder cycle')
            self.pill_handle = self.run_every(self.reminder, globals.now() + datetime.timedelta(seconds=1), self.repeat_every)
        else:
            self.log('Coffee is brewing, but reminders are switched off')

    def on_test(self, event_name, data, kwargs):
        self.on_coffee_started()

    def on_test2(self, event_name, data, kwargs):
        self.disarm('TEST2', [], {})

    def disarm(self, event_name, data, kwargs):
        if self.pill_handle:                     
            self.cancel_timer(self.pill_handle)
            self.pill_handle = None
        if self.vitamin_handle:
            self.cancel_timer(self.vitamin_handle)
            self.vitamin_handle = None
        if self.is_armed(TRIGGER1):
            self.turn_off(TRIGGER1)
            start_date = self.datetime() + datetime.timedelta(seconds=self.run_vitamin_after)
            self.log(f'Pill reminder disarmed, vitamin reminder armed for {start_date}')
            self.speak('Спасибо, таблетка учтена')
            self.vitamin_handle = self.run_every(self.reminder, start_date, self.repeat_every)
        elif self.is_armed(TRIGGER2):
            self.turn_off(TRIGGER2)
            self.log('Vitamin reminder disarmed')
            self.speak('Спасибо, витаминка учтена')
        else:
            self.log('nothing to disarm')
        
    def on_coffee(self, entity, attribute, old, new, kwargs):
        if new == 'on':
            self.on_coffee_started()

    def arm(self, kwargs):
        self.log('Pill reminder and vitamin reminder armed')
        self.turn_on(TRIGGER1)
        self.turn_on(TRIGGER2)

    def is_armed(self, trigger):
        return self.get_state(trigger) == 'on'

    def reminder(self, kwargs):
        if self.is_armed(TRIGGER1):
            self.log('Say pill reminder')
            self.speak('Напоминаю про таблетку')
        elif self.is_armed(TRIGGER2):
            self.log('Say vitamin reminder')
            self.speak('Напоминаю про витаминку')
        else:
            self.log('WARNING: Pill reminder is active, but nothing to say')
            