from log import log
from . import Level

import json


# Manages all levels in the game.
class WorldManager:
    def __init__(self, Manager):
        self.Manager = Manager
        self.levels = {}

        # Load list of defined levels.
        filename = Manager.config['files']['defined_levels']

        try:
            self.defined_levels = json.load(open(filename, 'r'))
            log('WorldManager', f'Loaded {filename}')
        except IOError:
            log('WorldManager', f'Failed to open {filename}', 'fatal error')
            exit()
        except json.decoder.JSONDecodeError:
            log(
                'WorldManager',
                f'Failed to parse {filename} (empty?)',
                'warning'
            )

        log('WorldManager', 'Initialized.')

    def addEntityToLevel(self, entity, level_id):
        level = self.getLevel(level_id)
        level.addEntity(entity)

    # Returns a position component set to the default starting area of the
    # game.
    def getDefaultPositionComp(self, entity):
        default_level = 'starting_area'
        level = self.getLevel(default_level)

        default_x = level.elements['spawn_tile']['x']
        default_y = level.elements['spawn_tile']['y']

        return self.Manager.ComponentManager.new(entity, 'position', {
            'on_level': default_level,
            'x': default_x,
            'y': default_y
        })

    def getLevel(self, id_):
        if id_ in self.levels:
            return self.levels[id_]
        else:
            if id_ not in self.defined_levels:
                log(
                    'WorldManager',
                    f'Level with ID [{id_}] is unknown!',
                    'error'
                )
                return

            try:
                level_data = json.load(open(self.defined_levels[id_], 'r'))
            except json.decoder.JSONDecodeError:
                log(
                    'WorldManager',
                    f'Failed to parse {self.defined_levels[id_]} (empty?)',
                    'warning'
                )

            self.levels[id_] = Level.Level(level_data)
            return self.levels[id_]

    def getLevelJSON(self, level_id):
        return self.getLevel(level_id).getAsJSON()
