"""
Wishes good morning via a Sonos speaker and gives a briefing on the actual Todoist tasks
"""
import appdaemon.plugins.hass.hassapi as hass

class Morning(hass.Hass):
    def initialize(self):
        self.listen_event(self.start_morning_routine, "AD.good_morning")
        self.tts = self.get_app('neosonos')
        self.log('morning_started')

    def start_morning_routine(self, event_name, data, kwargs):
        self.log('morning_fired')
        morning_message = self.get_state("sensor.todoist_morning_message")
        if morning_message:
            self.tts.speak(morning_message,volume=0.3)