import re
from datetime import datetime
import appdaemon.plugins.hass.hassapi as hass

DATE_PATTERN = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+ .*$)"
ERR_PATTERN = r"error|exception"
TRESHOLD = 3600
MAX_ERRORS = 10

class LogWatch(hass.Hass):
    def initialize(self):
        self.handle = self.run_every(self.check_log, self.datetime(), 15*60)
        self.messenger = self.get_app("messages")
        self.listen_event(self.receive_telegram_callback, 'telegram_callback')
        self.muted = True #!!!!!
        self.handle = None
        self.chat_id = self.args['chat_id']

    def snooze_for(self, delay):
        if self.handle:
            self.cancel_timer(handle)
            self.log('Timer reset')
        self.muted = True
        self.log('Log warnings muted for {}'.format(delay))
        self.handle = self.run_in(self.unmute, delay)

    def unmute(self, kwargs):
        self.muted = False
        self.log('Log warnings unmuted')
        self.handle = None

    def send_message(self, msg, chat_id, callback_id=None):
        if callback_id:
            self.call_service('telegram_bot/answer_callback_query',
                              message=msg,
                              callback_query_id=callback_id,
                              show_alert=False)

        keyboard = [[(u"Snooze for 1 hr", "/snooze1")]]
        self.call_service('telegram_bot/send_message',
                          target=chat_id,
                          message=msg,
                          disable_notification=True,
                          inline_keyboard=keyboard)

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
        if err_count > MAX_ERRORS and self.messenger and not self.muted:
            #self.messenger.alert()
            self.send_message('⚠ {} errors in the HA log'.format(err_count), [self.chat_id])

    def receive_telegram_callback(self, event_id, payload_event, *args):
        """Event listener for Telegram callback queries."""
        self.log('CALLBACK RECEIVED')
        assert event_id == 'telegram_callback'
        data_callback = payload_event['data']
        callback_id = payload_event['id']
        chat_id = payload_event['chat_id']

        if data_callback == '/snooze1':
            self.log('Error messages snoozed for 1 hour')
            self.send_message('Error messages snoozed for 1 hour', chat_id = chat_id, callback_id = callback_id)
            self.snooze_for(3600)
        else:
            self.log('Unknown command', level = "WARNING")
