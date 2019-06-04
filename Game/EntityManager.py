from log import log
from . import Entity

import json


# Manages all entities in the game world.
class EntityManager:
    def __init__(self, Manager):
        self.Manager = Manager
        self.entities = {}
        self.changed = []

        # Load preset data from file.
        self.presets = {
            'monsters': json.load(
                open(Manager.config['entity_data']['monsters'], 'r')
            )
        }

        log('EntityManager', 'Initialized.')

    # Creates a blank new entity and returns it.
    def new(self, preset=None):
        entity = Entity.Entity()
        self.entities[entity.id] = entity

        # If given a preset, set up its components.
        if preset:
            category = preset.split(':')[0]
            type_ = preset.split(':')[1]

            preset = self.presets[category][type_]

            for c in preset['components']:
                entity.addComponent(self.Manager.ComponentManager.new(
                    entity,
                    c,
                    preset['components'][c]
                ))

        if 'EntityManager' in self.Manager.monitors:
            for sid in self.Manager.monitors['EntityManager']:
                self.Manager.sio.emit('monitor update', {
                    'monitor': 'EntityManager',
                    'data': {
                        'n_entities': len(self.entities)
                    }
                }, room=sid)

        self.markChanged(entity.id)
        return entity

    # Marks an entity as changed.
    def markChanged(self, entity_id):
        if entity_id not in self.changed:
            self.changed.append(entity_id)

    def markDeleted(self, entity_id):
        if entity_id in self.entities:
            self.entities[entity_id].markDeleted()
            self.markChanged(entity_id)

    def get(self, entity_id):
        if entity_id in self.entities:
            return self.entities[entity_id]

    def getChanged(self):
        return self.changed

    def resetChanged(self):
        self.changed = []

    def delete(self, entity_id):
        del self.entities[entity_id]

        for l in self.Manager.WorldManager.levels:
            self.Manager.WorldManager.levels[l].delEntity(entity_id)

        log('EntityManager', f'Deleted entity#{entity_id}', 'debug(2)')
