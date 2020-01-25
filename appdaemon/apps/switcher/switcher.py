#encoding utf-8
import appdaemon.plugins.hass.hassapi as hass

class Switcher(hass.Hass):
    def initialize(self):
        self.switch_id = self.args['switch_id']
        if not self.switch_id.startswith('switch.'):
            raise Exception(f'switch_id should start from "switch." [{self.switch_id}]') 
        self.switch_name = self.args['switch_name']
        self.listen_event(self.on_call_service, event = "call_service")
        self.db = self.get_app('shelf')
        self.persistent = self.args.get('persistent', True)
        if not self.entity_exists(self.switch_id):
            state = self.db.get_value(self.switch_id, "off")
            self.log(f'Restore state of the switch {self.switch_id} to "{state}"')
            self.update_state(state)

    def update_state(self, state, **kwargs):
        if self.persistent:
            self.db.set_value(self.switch_id, state)
        self.set_state(self.switch_id, state = state, attributes = {"friendly_name":self.switch_name})
        
    def on_call_service(self,event_name,data, kwargs):
        if data['service'] in ['turn_on','turn_off']:
            if self.switch_id == data["service_data"]["entity_id"]:
                if data["service"] == "turn_off":
                    #self.log(self.switch_id + " switched off")
                    self.update_state('off')
                if data["service"] == "turn_on":
                    #self.log(self.switch_id + " switched on")
                    self.update_state('on')

