from log import log
from . import Component


# Manages all components of all entities in the game world.
class ComponentManager:
    def __init__(self, Manager):
        self.Manager = Manager
        self.components = {}

        log('ComponentManager', 'Initialized.')

    # Creates a new component of a type and returns it.
    # The default details of the component type will be loaded from file, but
    # will then be updated with the supplied data.
    def new(self, parent, type_, data):
        component = Component.Component(parent, type_, data)
        self.components[component.id] = component

        # If it is a position component, make sure the relevant level ahs the
        # entity added.
        if type_ == 'position':
            self.Manager.WorldManager.addEntityToLevel(
                parent,
                data['on_level']
            )

        return component
