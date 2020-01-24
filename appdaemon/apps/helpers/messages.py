#encoding utf-8
import appdaemon.plugins.hass.hassapi as hass

class Messenger(hass.Hass):
    def initialize(self):
        self.chat_id = self.args['chat_id']

    def sanitize(self, msg):
        return msg.replace('_','\\_')

    def alert(self, msg):
        self.call_service('telegram_bot/send_message',
                          target=self.chat_id,
                          message='⚠ {}'.format(self.sanitize(msg)),
                          disable_notification=True)

    def message(self, msg):
        self.call_service('telegram_bot/send_message',
                  target=self.chat_id,
                  message='ℹ {}'.format(self.sanitize(msg)),
                  disable_notification=True)

    def bell(self, msg):
        self.call_service('telegram_bot/send_message',
                  target=self.chat_id,
                  message='🔔 {}'.format(self.sanitize(msg)),
                  disable_notification=True)

