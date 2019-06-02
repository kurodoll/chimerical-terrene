from log import log
from . import Entity


# Manages all entities in the game world.
class EntityManager:
    def __init__(self):
        self.entities = {}
        log('EntityManager', 'Initialized.')

    # Creates a blank new entity and returns it.
    def new(self):
        entity = Entity.Entity()
        self.entities[entity.id] = entity

        return entity
