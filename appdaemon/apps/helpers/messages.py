#encoding utf-8
import appdaemon.plugins.hass.hassapi as hass

class Messenger(hass.Hass):
    def initialize(self):
        self.chat_id = self.args['chat_id']
        self.categories = self.args['categories']
        
    def sanitize(self, msg):
        return msg.replace('_','\\_')

    def is_enabled(self, category):
        if not category:
            return True
        if not category.startswith('switch.'):
            category = 'switch.'+category
        #assert (category in self.categories)
        return self.get_state(category) == 'on'

    def alert(self, msg, category=None):
        if not self.is_enabled(category):
            self.log(f'⚠ Suppressed message [{category}]:  {msg}', ascii_encode=False)
            return
        self.call_service('telegram_bot/send_message',
                        target=self.chat_id,
                        message='⚠ {}'.format(self.sanitize(msg)),
                        disable_notification=True)

    def message(self, msg, category=None):
        if not self.is_enabled(category):
            self.log(f'ℹ Suppressed message [{category}]: {msg}', ascii_encode=False)
            return
        self.call_service('telegram_bot/send_message',
                target=self.chat_id,
                message='ℹ {}'.format(self.sanitize(msg)),
                disable_notification=True)

    def bell(self, msg, category=None):
        if not self.is_enabled(category):
            self.log(f'🔔 Suppressed message [{category}]: {msg}', ascii_encode=False)
            return
        self.call_service('telegram_bot/send_message',
                target=self.chat_id,
                message='🔔 {}'.format(self.sanitize(msg)),
                disable_notification=True)

