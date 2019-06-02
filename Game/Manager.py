from . import EntityManager
from . import ComponentManager
from . import WorldManager


class Manager:
    def __init__(self):
        self.config = {
            'files': {
                'static_files': 'config/static_files.json'
            },
            'server': {
                'default_port': 3000
            }
        }

        self.EntityManager = EntityManager.EntityManager()
        self.ComponentManager = ComponentManager.ComponentManager()
        self.WorldManager = WorldManager.WorldManager(self)

    # Creates a new player character entity based on initial details.
    def newCharacter(self, details):
        character = self.EntityManager.new()

        # Give the entity the character's name.
        character.addComponent(self.ComponentManager.new(
            'name',
            {
                'name': details['name']
            }
        ))

        # Initialize the entity at the starting area.
        character.addComponent(self.WorldManager.getDefaultPositionComp())

        return character
