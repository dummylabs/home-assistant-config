import appdaemon.plugins.hass.hassapi as hass

class NeoSonos(hass.Hass):
    def initialize(self):
        self.entity = self.args['entity']
        self.tts = self.args['tts']
        self.dnd = self.get_app('dnd')
        self.opener_file_base = self.args['opener_file_base']
        self.delay = 2

    def _listen_player_state(self, entity, attribute, old, new, kwargs):
        self.restore()

    @property
    def volume(self):
        """Retrieve the audio player's volume."""
        return self.get_state(self.entity, attribute='volume_level')

    @volume.setter
    def volume(self, value):
        """Set the audio player's volume."""
        self.call_service(
            'media_player/volume_set',
            entity_id=self.entity,
            volume_level=value)

    def snapshot(self):
        self.log('SNAPSHOT SPEAKER STATE')
        self.call_service(
            'sonos/snapshot',
            entity_id=self.entity,
            with_group=False)

    def restore(self):
        self.log('RESTORE SPEAKER STATE')
        self.call_service(
            'sonos/restore',
            entity_id=self.entity,
            with_group=False)

    def play_file(self, url):
        self.call_service(
            'media_player/play_media',
            entity_id=self.entity,
            media_content_id=url,
            media_content_type='music')

    def pause(self):
        self.call_service('media_player/media_pause', entity_id=self.entity)

    def play(self):
        self.call_service('media_player/media_play', entity_id=self.entity)

    def _speak_cb(self, kwargs):
        sonos_player = kwargs['sonos_player']
        text = kwargs['text']
        self.call_service(
            self.tts,
            entity_id=str(sonos_player),
            message=text)

    def speak(self, text, volume=0.5, opener='e-mail.mp3'):
        if self.dnd.is_set():
            volume = 0.2
        self.snapshot()
        self.volume = volume
        self.play_file(self.opener_file_base + opener)
        self.run_in(
            self._speak_cb,
            self.delay,
            sonos_player=self.entity,
            text=text,
            volume=volume)

        self.listen_state(self._listen_player_state, self.entity, duration=5, old='playing',  new='paused', oneshot=True)
