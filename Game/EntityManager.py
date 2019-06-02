from log import log
from . import Entity


# Manages all entities in the game world.
class EntityManager:
    def __init__(self, Manager):
        self.Manager = Manager
        self.entities = {}

        log('EntityManager', 'Initialized.')

    # Creates a blank new entity and returns it.
    def new(self):
        entity = Entity.Entity()
        self.entities[entity.id] = entity

        if 'EntityManager' in self.Manager.monitors:
            for sid in self.Manager.monitors['EntityManager']:
                self.Manager.sio.emit('monitor update', {
                    'monitor': 'EntityManager',
                    'data': {
                        'n_entities': len(self.entities)
                    }
                }, room=sid)

        return entity
