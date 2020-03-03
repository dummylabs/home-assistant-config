"""
The app to send a notification when the home presence state of a specified person is changed
Can be controlled by a notification category switch (messages app).
"""

import appdaemon.plugins.hass.hassapi as hass

class TrackPersons(hass.Hass):
  def initialize(self):
    self.msg = self.get_app('messages')
    self.listen_state(self.state_handler, 'person')

  def state_handler(self, entity, attribute, old, new, kwargs):
    tracked_states = ['home','not_home']
    self.log(f'{entity=} {old=} {new=}')
    if old in tracked_states or new in tracked_states:
        name = self.get_state(entity_id = entity, attribute = 'friendly_name')
        if entity == 'person.vika':
            message = f'{name} пришла домой' if new == 'home' else f'{name} вышла из дома'
        else:
            message = f'{name} пришёл домой' if new == 'home' else f'{name} вышел из дома'
        self.msg.message(f'{message} {old=} {new=}', category='notify_person_tracking')
    else:
        self.log(f'states {old}->{new} are not supported')
