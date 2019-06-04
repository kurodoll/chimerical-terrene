from log import log
import random

id_ = 0


def nextID():
    global id_

    ret_id = id_
    id_ += 1

    return ret_id


class Entity:
    def __init__(self):
        self.id = nextID()
        self.components = {}
        self.deleted = False

        log(f'Entity#{self.id}', 'Created.', 'debug')

    # If the entity is a mob, this updates them (movement, etc.)
    def updateMob(self, WorldManager):
        if 'ai' in self.components:
            movement = self.components['ai'].get('movement')

            if movement == 'random':
                x = self.getComp('position').get('x')
                y = self.getComp('position').get('y')

                adjacent_spots = [
                    {'x': x - 1, 'y': y - 1},
                    {'x': x, 'y': y - 1},
                    {'x': x + 1, 'y': y - 1},
                    {'x': x - 1, 'y': y},
                    {'x': x + 1, 'y': y},
                    {'x': x - 1, 'y': y + 1},
                    {'x': x, 'y': y + 1},
                    {'x': x + 1, 'y': y + 1}
                ]

                possible_spots = []

                for a in adjacent_spots:
                    if WorldManager.validMove(self.getComp('position').get('on_level'), a):  # noqa
                        possible_spots.append(a)

                WorldManager.Manager.queueAction(
                    0,
                    'move',
                    {
                        'entity': self.id,
                        'coord': possible_spots[random.randint(
                            0,
                            len(possible_spots) - 1
                        )]
                    }
                )

    # Adds a component to the entity. Only one component of each type can
    # exist.
    def addComponent(self, component):
        self.components[component.type] = component

        log(
            f'Entity#{self.id}',
            f'Component of type {component.type} added.',
            'debug'
        )

    def getComp(self, type_):
        if type_ in self.components:
            return self.components[type_]

    def getCompsAsJSON(self):
        comps = {}

        for c in self.components:
            comps[c] = self.components[c].toJSON()

        return comps

    def toJSON(self):
        return {
            'id': self.id,
            'components': self.getCompsAsJSON(),
            'deleted': self.deleted
        }

    def markDeleted(self):
        self.deleted = True
