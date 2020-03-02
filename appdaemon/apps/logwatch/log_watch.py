"""
Counts the error messages in the HA log for the last hour and sends an alert when
the it raises above the treshold.
"""
import re
from datetime import datetime
import appdaemon.plugins.hass.hassapi as hass
import globals

DATE_PATTERN = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+ .*$)"
ERR_PATTERN = r"error|exception"
TRESHOLD = 3600
MAX_ERRORS = 10

class LogWatch(hass.Hass):
    def initialize(self):
        self.handle = self.run_every(self.check_log, globals.now(), 15*60)
        self.messenger = self.get_app("messages")
        self.chat_id = self.args['chat_id']

    def check_log(self, kwargs):
        err_count = 0
        now = datetime.now()
        with open ('/config/home-assistant.log', 'rt') as myfile:
            for myline in myfile:                 
                z = re.match(DATE_PATTERN, myline, re.MULTILINE)
                if z:
                    dt = datetime.strptime(z.groups()[0], '%Y-%m-%d %H:%M:%S')
                    time_passed = (now - dt).total_seconds()
                    if time_passed < TRESHOLD:
                        err = re.match(ERR_PATTERN, z.groups()[1], re.IGNORECASE)
                        if err:
                            err_count += 1
        self.set_state("sensor.log_errors", state = err_count, attributes = {"friendly_name": "Errors in log", "unit_of_measurement": 'errors'})
        if err_count > MAX_ERRORS:
            self.messenger.alert(f'Too many errors in home_assistant.log: {err_count}', category='notify_log_errors')
