"""Define an app to manage our Sonos players."""

# pylint: disable=too-many-arguments,attribute-defined-outside-init

import appdaemon.plugins.hass.hassapi as hass


class SonosSpeaker(hass.Hass):
    """Define a class to represent a Sonos speaker."""

    def __str__(self):
        """Define a string representation of the speaker."""
        return self.entity

    def initialize(self):
        """Initialize."""
        self._last_snapshot_included_group = False
        self.entity = self.args['entity']

        self.sonos_manager = self.get_app('sonos_manager')
        self.sonos_manager.register_entity(self)

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

    def pause(self):
        """Pause."""
        self.call_service('media_player/media_pause', entity_id=self.entity)

    def play(self):
        """Play."""
        self.call_service('media_player/media_play', entity_id=self.entity)

    def play_file(self, url):
        """Play an audio file at a defined URL."""
        self.call_service(
            'media_player/play_media',
            entity_id=self.entity,
            media_content_id=url,
            media_content_type='music')

    def restore(self):
        """Restore the previous snapshot of this entity."""
        self.call_service(
            'sonos/restore',
            entity_id=self.entity,
            with_group=self._last_snapshot_included_group)

    def snapshot(self, include_grouping=True):
        """Snapshot this entity."""
        self._last_snapshot_included_group = include_grouping
        self.call_service(
            'sonos/snapshot',
            entity_id=self.entity,
            with_group=include_grouping)


class SonosManager(hass.Hass):
    """Define a class to represent the Sono manager."""

    def initialize(self):
        """Initialize."""
        self._last_snapshot_included_group = False
        self.entities = []

    def group(self, entity_list=None):
        """Group a list of entities together (default: all)."""
        entities = entity_list
        if not entity_list:
            entities = [entity for entity in self.entities]

        master = entities.pop(0)

        if not entities:
            self.log(
                'Refusing to group only one entity: {0}'.format(master),
                level='WARNING')

        self.call_service(
            'sonos/join',
            master=master.entity,
            entity_id=[str(e) for e in entities])

        return master

    def register_entity(self, speaker_object):
        """Register a Sonos entity object."""
        if speaker_object in self.entities:
            self.log('Entity already registered; skipping: {0}'.format(
                speaker_object))
            return

        self.entities.append(speaker_object)

    def restore_all(self):
        """Restore the previous snapshot of all entities."""
        self.call_service(
            'sonos/restore',
            entity_id=[str(e) for e in self.entities],
            with_group=self._last_snapshot_included_group)

    def snapshot_all(self, include_grouping=True):
        """Snapshot all registered entities simultaneously."""
        self._last_snapshot_included_group = include_grouping
        self.call_service(
            'sonos/snapshot',
            entity_id=[str(e) for e in self.entities],
            with_group=include_grouping)

    def ungroup_all(self):
        """Return all speakers to "individual" status."""
        self.call_service(
            'sonos/unjoin',
            entity_id=[str(e) for e in self.entities])