from . import EntityManager
from . import ComponentManager


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

    # Creates a new player character entity based on initial details.
    def newCharacter(self, details):
        character = self.EntityManager.new()

        character.addComponent(self.ComponentManager.new(
            'name',
            {
                'name': details['name']
            }
        ))

        return character
