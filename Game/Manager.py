from . import EntityManager
from . import ComponentManager
from . import WorldManager


class Manager:
    def __init__(self, sio):
        self.sio = sio

        self.config = {
            'files': {
                'static_files': 'config/static_files.json',
                'defined_levels': 'Game/data/world/defined_levels.json'
            },
            'server': {
                'default_port': 3000
            }
        }

        self.EntityManager = EntityManager.EntityManager(self)
        self.ComponentManager = ComponentManager.ComponentManager(self)
        self.WorldManager = WorldManager.WorldManager(self)

        self.monitors = {}

    # Creates a new player character entity based on initial details.
    def newCharacter(self, details):
        character = self.EntityManager.new()

        # Give the entity the character's name.
        character.addComponent(self.ComponentManager.new(
            character,
            'name',
            {
                'name': details['name']
            }
        ))

        # Initialize the entity at the starting area.
        character.addComponent(
            self.WorldManager.getDefaultPositionComp(character)
        )

        # Give the entity a sprite.
        character.addComponent(self.ComponentManager.new(
            character,
            'sprite',
            {
                'sprite': 'player'
            }
        ))

        return character

    # Set up a monitor for some data in the game, that will be sent to the
    # specified client whenever the data is changed.
    def addMonitor(self, for_data, sid):
        if for_data in self.monitors:
            if sid not in self.monitors[for_data]:
                self.monitors[for_data].append(sid)
        else:
            self.monitors[for_data] = [sid]

        # Emit initial data.
        if for_data.split(':')[0] == 'level':
            self.sio.emit('monitor update', {
                'monitor': for_data,
                'data': self.WorldManager.getLevelJSON(for_data.split(':')[1])
            }, room=sid)
