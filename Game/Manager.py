from . import EntityManager
from . import ComponentManager
from . import WorldManager


class Manager:
    def __init__(self, sio):
        self.sio = sio

        self.config = {
            'files': {
                'static_files': 'config/static_files.json',
                'defined_levels': 'Game/data/world/defined_levels.json',
            },
            'server': {
                'default_port': 3000
            },
            'entity_data': {
                'monsters': 'Game/data/entities/monsters.json'
            }
        }

        self.EntityManager = EntityManager.EntityManager(self)
        self.ComponentManager = ComponentManager.ComponentManager(self)
        self.WorldManager = WorldManager.WorldManager(self)

        self.action_queue = []
        self.links = {}
        self.monitors = {}

    # Adds an action to the queue of changes to the world to be processed.
    def queueAction(self, sid, type_, details):
        self.action_queue.append({
            'sid': sid,
            'type': type_,
            'details': details
        })

    # Process the next action in the queue.
    def processActions(self):
        while len(self.action_queue):
            action = self.action_queue.pop(0)

            if action['type'] == 'move':
                # Get the entity that is trying to be moved.
                entity = self.EntityManager.get(action['details']['entity'])

                # Ensure that the entity is user controllable by the action
                # taker.
                if entity.getComp('user_controlled') and entity.getComp('user_controlled').get('owner') == action['sid']:  # noqa
                    # Get the direction and try to move the entity.
                    dir_ = action['details']['dir']
                    pos = entity.getComp('position')

                    old_x = pos.get('x')
                    old_y = pos.get('y')

                    if dir_ == '1':
                        pos.setValue('x', pos.get('x') - 1)
                        pos.setValue('y', pos.get('y') + 1)
                    elif dir_ == '2':
                        pos.setValue('y', pos.get('y') + 1)
                    elif dir_ == '3':
                        pos.setValue('x', pos.get('x') + 1)
                        pos.setValue('y', pos.get('y') + 1)
                    elif dir_ == '4':
                        pos.setValue('x', pos.get('x') - 1)
                    elif dir_ == '6':
                        pos.setValue('x', pos.get('x') + 1)
                    elif dir_ == '7':
                        pos.setValue('x', pos.get('x') - 1)
                        pos.setValue('y', pos.get('y') - 1)
                    elif dir_ == '8':
                        pos.setValue('y', pos.get('y') - 1)
                    elif dir_ == '9':
                        pos.setValue('x', pos.get('x') + 1)
                        pos.setValue('y', pos.get('y') - 1)

                    if not self.WorldManager.validMove(pos.get('on_level'), {
                        'x': pos.get('x'),
                        'y': pos.get('y')
                    }):
                        pos.setValue('x', old_x)
                        pos.setValue('y', old_y)
                    else:
                        self.EntityManager.markChanged(entity.id)

    # Link a client to a level, meaning they will be sent any changes made to
    # the level.
    def link(self, sid, level_id):
        if level_id in self.links:
            self.links[level_id].append(sid)
        else:
            self.links[level_id] = [sid]

    # Send out all entity changes to clients.
    def emitUpdates(self):
        changes = self.EntityManager.getChanged()
        self.EntityManager.resetChanged()

        for c in changes:
            ent = self.EntityManager.get(c)
            pos = ent.getComp('position')

            if pos:
                level_id = pos.get('on_level')

                if level_id in self.links:
                    for sid in self.links[level_id]:
                        self.sio.emit('entity update', ent.toJSON(), room=sid)

            if ent.deleted:
                self.EntityManager.delete(c)

    # Creates a new player character entity based on initial details.
    def newCharacter(self, details, sid):
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

        # Mark the entity as controlled by the user.
        character.addComponent(self.ComponentManager.new(
            character,
            'user_controlled',
            {
                'owner': sid
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
