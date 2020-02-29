import appdaemon.plugins.hass.hassapi as hass
import datetime
import globals
import timeago

class StateSaver(hass.Hass):
    def initialize(self):
        self.path = self.args['shelf_path']
        self.run_every(self.update_all_entities, globals.now(), self.args['update_period'])
        self.listen_state(self.state_handler)

    def update_all_entities(self, kwargs):
        for entity_id in self.args['entities']:
            date = globals.get_value(self.path, entity_id)
            serialize = not date
            if serialize:
                date = datetime.datetime.now()
            self.update_entity(entity_id, date, serialize=serialize)

    def update_entity(self, entity_id, date, serialize=True):
        entity_name = f"{entity_id}_last_changed"
        human_readable_ts = timeago.format(date, datetime.datetime.now(), 'ru').replace('назад','')
        self.set_state(entity_name, state = human_readable_ts, attributes = {'timestamp':date.isoformat()})
        if serialize:
            globals.set_value(self.path, entity_id, date)

    def seconds_since_changed(self, entity_id):
        entity_name = f"{entity_id}_last_changed"
        date = globals.get_value(self.path, entity_id)
        if date:
            return int((self.datetime()-date).total_seconds())
        else:
            return None

    def state_handler(self, entity, attribute, old, new, kwargs):
        if entity in self.args['entities'] and old != new:
            self.update_entity(entity, datetime.datetime.now())
