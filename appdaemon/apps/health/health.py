import appdaemon.plugins.hass.hassapi as hass
import errors
import datetime
import globals

class HealthMonitor(hass.Hass):
    def initialize(self):
        self.messenger = self.get_app('messages')
        self.monitored_entities = self.args['monitored_entities'].split(",")
        self.run_every(self.check_states, globals.now(), 15*60)
        
    def check_states(self, kwargs): 
        errors = []
        tracker_offline = True
        for entity in self.monitored_entities:
            attrs = self.get_state(entity, attribute='all')
            state = attrs.get('state', 'not_home') if attrs else 'not_home'
            if state in ['not_home','unavailable']:
                msg =attrs['attributes']['friendly_name'] + ' is offline!' if attrs else 'Unknown entity:{}'.format(entity) 
                errors.append(msg)
                #self.log(msg)
            if state == 'home':
                tracker_offline = False
                #self.log(entity)
        
        if tracker_offline:
            self.messenger.alert('Keenetic device tracker not responding, all devices are offline')
        else:
            for e in errors:
                self.messenger.alert(e) 
                                                              