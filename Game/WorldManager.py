from log import log


# Manages all levels in the game.
class WorldManager:
    def __init__(self, Manager):
        self.Manager = Manager
        self.levels = {}

        log('WorldManager', 'Initialized.')

    # Returns a position component set to the default starting area of the
    # game.
    def getDefaultPositionComp(self):
        return self.Manager.ComponentManager.new('position', {
            'on_level': 'starting area',
            'x': 0,
            'y': 0
        })

    def getLevel(self, name):
        if name in self.levels:
            return self.levels[name]
        else:
            pass  # TODO: Load level here.
