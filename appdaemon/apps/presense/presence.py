#encoding utf-8
import appdaemon.plugins.hass.hassapi as hass
import datetime

settings = {
    'dima':['input_select.dima_status_dropdown', 'person.dima'],
    'vika':['input_select.vika_status_dropdown', 'person.vika']
}

DELAY = 5 * 60
EXTENDED_DELAY = 24 * 60 * 60

class NonBinaryPresence(hass.Hass):
    def initialize(self):
        self.handles = {}
        self.init_dropdowns()
        self.listen_state(self.tracker_handler, 'person')
        self.listen_state(self.input_handler, 'input_select')
        self.messenger = self.get_app('messages')

    # set initial dropdown values according to trackers state
    def init_dropdowns(self):
        for person in settings:
            state = self.get_state(settings[person][1])
            dropdown_state = 'home' if state == 'home' else 'away'
            self.change_state(person, dropdown_state)

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
            self.log(f'Error: trying to reset non-existing handle for person {person}')

    # change state of fake sensor and cancel all delayed changes if any
    def change_state(self, person, state):
        self.log(f'state_change called. for {person} to {state}')
        handle = self.get_handle(person)
        if handle:
            self.log(f'Cancel running task handle for {person}')
            self.cancel_timer(handle)
            #remove delayed_state_change handles for the person if we have any
            self.set_handle(person, None)
        self.select_option(settings[person][0], state)
        #self.log('Status of {} changed to {}'.format(person, state))

    # handle changes of fake sensor
    # schedule state change after specific time, e.g. away->extended_away
    def input_handler(self, entity, attribute, old, new, kwargs):
        person = self.get_person(entity)
        if person:
            self.log(f'dropdown {entity} changed from {old} to {new}')
            if new == 'away':
                self.set_handle(person, self.run_in(self.delayed_state_change, EXTENDED_DELAY, person=person, state='extended away'))
            if new == 'just arrived':
                self.messenger.message(f'Welcome home, {person}!!!')
                

    # handle changes of device tracker sensor
    # schedule state change after specific time, e.g. just_arrived->home
    def tracker_handler(self, entity, attribute, old, new, kwargs):
        person = self.get_person(entity)
        if new == old:
            self.log(f'tracker {entity} state remains {new} for person: {person}')
        self.log(f'tracker {entity} changed from {old} to {new}. person: {person}')
        if not person:
            return
        prev = self.get_state(settings[person][0])
        self.log(f'previous state of the {person} is {prev}')
        if new == 'home':
            if prev == 'just left':
                self.change_state(person, 'home')
            else:
                self.change_state(person, 'just arrived')
                self.set_handle(person, self.run_in(self.delayed_state_change, DELAY, person=person, state='home'))
        else: # consider away, moving and driving as away 
            if prev == 'home':
                self.change_state(person, 'just left')
                self.set_handle(person, self.run_in(self.delayed_state_change, DELAY, person=person, state='away'))
    
    def delayed_state_change(self, kwargs):
        self.log(f'Delayed change applied with kwargs:{kwargs}')
        self.change_state(kwargs['person'], kwargs['state'])
