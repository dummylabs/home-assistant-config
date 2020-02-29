#encoding utf-8
import appdaemon.plugins.hass.hassapi as hass
import datetime

settings = {
    'dima':['input_select.dima_status_dropdown', 'person.dima'],
    'vika':['input_select.vika_status_dropdown', 'person.vika']
}

presence_labels = {
    'nobody_home': 'никого нет дома',
    'somebody_home': 'кто-то есть дома',
    'everybody_home': 'все дома'
}

global_state = 'sensor.presence_status'

DELAY = 5 * 60
EXTENDED_DELAY = 24 * 60 * 60

class NonBinaryPresence(hass.Hass):
    def initialize(self):
        self.handles = {}
        self.init_dropdowns()
        self.update_global_presence({})
        self.listen_state(self.tracker_handler, 'person')
        self.listen_state(self.input_handler, 'input_select')
        self.messenger = self.get_app('messages')

    # set initial dropdown values according to trackers state
    def init_dropdowns(self):
        for person in settings:
            state = self.get_state(settings[person][1])
            dropdown_state = 'home' if state == 'home' else 'away'
            self.change_state(person, dropdown_state)

    def update_global_presence(self, kwargs):
        states = []
        for person in settings:
            states.append(self.get_state(settings[person][0]))
        #states = ['away','away']
        unique_states = set(states)
        
        final = 'unknown'
        if 'home' in unique_states:
            final = 'everybody_home' if len(unique_states) == 1 else 'somebody_home'
        elif 'away' in unique_states and len(unique_states) == 1:
            final = 'nobody_home'
        
        self.set_state(global_state, state=presence_labels.get(final, final), attributes={'friendly_name':'Статус присутствия'})
        self.log(f'{states=} {unique_states=} {final=}', level='DEBUG')
        if final != 'unknown':
            self.fire_event(f'ad.presence.{final}')

    def get_person(self, entity):
        for person in settings:
            if entity in settings[person]:
                return person
        return None
        
    def get_handle(self, person):
        return self.handles.get(person, None)

    def set_handle(self, person, handle):
        if handle:
            self.handles[person] = handle
        elif person in self.handles:
            del self.handles[person]
        else:
            self.log(f'Error: trying to reset non-existing handle for person {person}', level='DEBUG')

    # change state of fake sensor and cancel all delayed changes if any
    def change_state(self, person, state):
        #self.log(f'state_change called. for {person} to {state}')
        handle = self.get_handle(person)
        if handle:
            self.log(f'Cancel running task handle for {person}', level='DEBUG')
            self.cancel_timer(handle)
            #remove delayed_state_change handles for the person if we have any
            self.set_handle(person, None)
        self.select_option(settings[person][0], state)
        self.run_in(self.update_global_presence, 3)

    # handle changes of fake sensor
    # schedule state change after specific time, e.g. away->extended_away
    def input_handler(self, entity, attribute, old, new, kwargs):
        person = self.get_person(entity)
        if person:
            self.log(f'dropdown {entity} changed from {old} to {new}')
            if new == 'away':
                self.set_handle(person, self.run_in(self.delayed_state_change, EXTENDED_DELAY, person=person, state='extended away'))

    # handle changes of device tracker sensor
    # schedule state change after specific time, e.g. just_arrived->home
    def tracker_handler(self, entity, attribute, old, new, kwargs):
        person = self.get_person(entity)
        if new == old or not person:
            return
        self.log(f'tracker {entity} changed from {old} to {new}. person: {person}')
        prev = self.get_state(settings[person][0])
        self.log(f'previous state of the {person} is {prev}', level='DEBUG')
        if new == 'home':
            if prev == 'just left':
                self.change_state(person, 'home')
            else:
                self.change_state(person, 'just arrived')
                self.set_handle(person, self.run_in(self.delayed_state_change, DELAY, person=person, state='home'))
        elif prev == 'home': # consider away, moving and driving as not_home 
            self.change_state(person, 'just left')
            self.set_handle(person, self.run_in(self.delayed_state_change, DELAY, person=person, state='away'))
    
    def delayed_state_change(self, kwargs):
        self.log(f'Delayed change applied with kwargs:{kwargs}', level='DEBUG')
        self.change_state(kwargs['person'], kwargs['state'])
