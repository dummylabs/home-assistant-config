#encoding utf-8
import appdaemon.plugins.hass.hassapi as hass

class Messenger(hass.Hass):
    def initialize(self):
        self.chat_id = self.args['chat_id']
        self.categories = self.args['categories']
        #self.create_switches(self.categories)
        #self.listen_event(self.on_call_service, event = "call_service")
        

    def create_switches(self, categories):
        for switch in categories:
            switch_id = switch
            switch_name = categories[switch]['name']
            if not self.entity_exists(switch_id):
                self.set_state(switch_id, state = "off", attributes = {"friendly_name":switch_name})
            #self.listen_event(self.change_state, event = "call_service")

    def sanitize(self, msg):
        return msg.replace('_','\\_')

    def is_enabled(self, category):
        if not category:
            return True
        if not category.startswith('switch.'):
            category = 'switch.'+category
        assert (category in self.categories)
        return self.get_state(category) == 'on'

    def alert(self, msg, category=None):
        if not self.is_enabled(category):
            self.log(f'Suppressed message: ⚠ {msg}', ascii_encode=False)
            return
        self.call_service('telegram_bot/send_message',
                        target=self.chat_id,
                        message='⚠ {}'.format(self.sanitize(msg)),
                        disable_notification=True)

    def message(self, msg, category=None):
        if not self.is_enabled(category):
            self.log(f'Suppressed message: ℹ {msg}', ascii_encode=False)
            return
        self.call_service('telegram_bot/send_message',
                target=self.chat_id,
                message='ℹ {}'.format(self.sanitize(msg)),
                disable_notification=True)

    def bell(self, msg, category=None):
        if not self.is_enabled(category):
            self.log(f'Suppressed message 🔔 {msg}', ascii_encode=False)
            return
        self.call_service('telegram_bot/send_message',
                target=self.chat_id,
                message='🔔 {}'.format(self.sanitize(msg)),
                disable_notification=True)

    def on_call_service(self,event_name,data, kwargs):
        if data['service'] in ['turn_on','turn_off']:
            entity_id = data["service_data"]["entity_id"]
            if entity_id in self.categories:
                if data["service"] == "turn_off":
                    self.log(entity_id + "switched off")
                    self.set_state(entity_id, state = "off")
                if data["service"] == "turn_on":
                    self.log(entity_id + "switched on")
                    self.set_state(entity_id, state = "on")
                #self.log(self.nofification_enabled(entity_id))

