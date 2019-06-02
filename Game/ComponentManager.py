from . import Component


# Manages all components of all entities in the game world.
class ComponentManager:
    def __init__(self):
        self.components = {}

    # Creates a new component of a type and returns it.
    # The default details of the component type will be loaded from file, but
    # will then be updated with the supplied data.
    def new(self, type_, data):
        component = Component.Component(type_, data)
        self.components[component.id] = component

        return component
