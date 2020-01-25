import appdaemon.plugins.hass.hassapi as hass

class NeoSonos(hass.Hass):
    def initialize(self):
        self.entity = self.args['entity']
        self.tts = self.args['tts']
        self.dnd = self.get_app('dnd')
        self.opener_file_base = self.args['opener_file_base']
        self._snapshot = False
        self.listen_state(self._listen_player_state, self.entity, duration=5, old='playing',  new='paused')
        self.dnd_volume = self.args['dnd_volume']
        self.volume = self.args['volume']
        self.delay = self.args['opener_delay']
        self.opener = self.args['opener']


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
        self._snapshot = True
        self.call_service(
            'sonos/snapshot',
            entity_id=self.entity,
            with_group=False)

    def restore(self):
        if self._snapshot:
            self._snapshot = False
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
        

    def speak(self, text, volume=None, opener=None):
        opener = opener or self.opener
        volume = volume or self.volume
        if self.dnd.is_set():
            volume = self.dnd_volume
        
        self.snapshot()
        self.volume = volume
        path = self.opener_file_base + opener
        self.log(f'{path}')
        self.play_file(self.opener_file_base + opener)
        self.run_in(
            self._speak_cb,
            self.delay,
            sonos_player=self.entity,
            text=text,
            volume=volume)
        
