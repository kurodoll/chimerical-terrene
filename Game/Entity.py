from log import log

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

        log(f'Entity#{self.id}', 'Created.', 'debug')

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
