"""Define an app for working with TTS (over Sonos)."""
# https://gist.github.com/bachya/60df6a8f55f159649aae5bbda144ccde
# pylint: disable=attribute-defined-outside-init,too-few-public-methods
# pylint: disable=unused-argument

import appdaemon.plugins.hass.hassapi as hass

class TTS(hass.Hass):
    """Define a class to represent the app."""

    # --- INITIALIZERS --------------------------------------------------------
    def initialize(self):
        """Initialize."""
        self.delay = 2
        self._snapshots = 0
        self._last_spoken_text = None
        self._last_spoken_volume = None
        self.opener_file_base = self.args['opener_file_base']
        self.service = self.args['service']
        self.sonos_manager = self.get_app('sonos_manager')
        self.register_endpoint(self._tts_endpoint, 'tts')
        self.listen_state(self._listen_player_state, 'media_player.kitchen', duration=5, old='playing',  new='paused')

    def _listen_player_state(self, entity, attribute, old, new, kwargs):
        self.log('PLAYER STATE CHANGED to {}'.format(new))
        self._restore()

    def _snapshot(self):
        if self._snapshots == 0:
            self._snapshots = 1
            self.sonos_manager.snapshot_all()
            self.log('SNAPSHOT CREATED')

    def _restore(self):
        if self._snapshots == 1:
            self._snapshots = 0
            self.sonos_manager.restore_all()
            self.log('SNAPSHOT RESTORED')

    # --- ENDPOINTS -----------------------------------------------------------
    def _tts_endpoint(self, data):
        """Define an API endpoint to handle incoming TTS requests."""
        self.log('Received TTS data: {}'.format(data), level='DEBUG')
        if 'text' not in data:
            self.error('No TTS data provided')
            return '', 502

        self.speak(data['text'])
        response = {"status": "ok", "message": data['text']}
        return response, 200

    # --- CALLBACKS -----------------------------------------------------------
    def _calculate_ending_duration_cb(self, kwargs):
        """Calculate how long the TTS should play."""
        master_sonos_player = kwargs['master_sonos_player']

        self.run_in(
            self._end_cb,
            self.get_state(
                str(master_sonos_player), attribute='media_duration'),
            master_sonos_player=master_sonos_player)

    def _end_cb(self, kwargs):
        """Restore the Sonos to its previous state after speech is done."""
        master_sonos_player = kwargs['master_sonos_player']
        #master_sonos_player.play_file(OPENER_FILE_URL)
        self.run_in(self._restore_cb, self.delay*2)

    def _restore_cb(self, kwargs):
        """Restore the Sonos to its previous state after speech is done."""
        self.sonos_manager.restore_all()

    def _speak_cb(self, kwargs):
        """Restore the Sonos to its previous state after speech is done."""
        master_sonos_player = kwargs['master_sonos_player']
        text = kwargs['text']

        self.call_service(
            self.service,
            entity_id=str(master_sonos_player),
            message=text)

        #self.run_in(
        #    self._calculate_ending_duration_cb,
        #    1,
        #    master_sonos_player=master_sonos_player)

    # --- HELPERS -------------------------------------------------------------
    def repeat(self):
        """Repeat the last thing that was spoken."""
        if self._last_spoken_text:
            self.log('Repeating over TTS: {0}'.format(self._last_spoken_text))
            self.speak(self._last_spoken_text, self._last_spoken_volume)

    def speak(self, text, volume=0.5, opener='e-mail.mp3'):
        """Speak the provided text through the Sonos (pausing as needed)."""
        if self.get_state('input_boolean.mode_do_not_disturb') == 'on':
            self.log('Speaking over TTS [DND mode]: {0}'.format(text))
            volume = 0.2
        else:
            self.log('Speaking over TTS: {0}'.format(text))
            #volume = 0.5

        self._snapshot()
        ##self.sonos_manager.snapshot_all()
        ###master_sonos_player = self.sonos_manager.group()
        master_sonos_player = self.sonos_manager.entities[0]
        master_sonos_player.volume = volume
        master_sonos_player.play_file(self.opener_file_base + opener)

        self.run_in(
            self._speak_cb,
            self.delay,
            master_sonos_player=master_sonos_player,
            text=text,
            volume=volume)

        self._last_spoken_text = text
        self._last_spoken_volume = volume
