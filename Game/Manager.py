from . import EntityManager
from . import ComponentManager
from . import WorldManager
from . import InteractionManager
from . import Entity


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
        self.InteractionManager = InteractionManager.InteractionManager(self)

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
                if action['sid'] == 0 or (entity.getComp('user_controlled') and entity.getComp('user_controlled').get('owner') == action['sid']):  # noqa
                    pos = entity.getComp('position')

                    old_x = pos.get('x')
                    old_y = pos.get('y')

                    if 'coord' in action['details']:
                        pos.setValue('x', action['details']['coord']['x'])
                        pos.setValue('y', action['details']['coord']['y'])
                    else:
                        # Get the direction and try to move the entity.
                        dir_ = action['details']['dir']

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

                    res = self.WorldManager.validMove(pos.get('on_level'), {
                        'x': pos.get('x'),
                        'y': pos.get('y')
                    }, entity.id)

                    if res == 'valid':
                        self.EntityManager.markChanged(entity.id)
                    else:
                        # Reset the position of the entity back to where it
                        # was.
                        pos.setValue('x', old_x)
                        pos.setValue('y', old_y)

                        # If moving onto an entity, attack it.
                        if isinstance(res, Entity.Entity):
                            # But disallow this if it's already in combat.
                            if (not res.combat_status['in_combat']) or (entity.id in res.combat_status['with']):  # noqa
                                self.queueAction(
                                    action['sid'],
                                    'attack',
                                    {
                                        'attacker': entity,
                                        'defender': res
                                    }
                                )

                # If the entity is in combat, its combatants get to make a
                # move now. But this should only happen when it's a player
                # making this move.
                if entity.combat_status['in_combat'] and entity.getComp('type').get('type') == 'player':  # noqa
                    for e in entity.combat_status['with']:
                        self.EntityManager.get(e).updateMob(
                            self.WorldManager,
                            True
                        )

            # If an entity goes down some stairs, we have to change the level
            # they're on.
            elif action['type'] == 'stairs down':
                # Get the entity that is trying to be moved.
                entity = self.EntityManager.get(action['details']['entity'])

                # Ensure that the entity is user controllable by the action
                # taker.
                if action['sid'] == 0 or (entity.getComp('user_controlled') and entity.getComp('user_controlled').get('owner') == action['sid']):  # noqa
                    pos = entity.getComp('position')
                    level = self.WorldManager.getLevel(pos.get('on_level'))

                    if 'stairs_down' in level.getTile(pos.get('x'), pos.get('y')).attributes and 'stairs down' in level.elements:  # noqa
                        target = level.elements['stairs down']['target']

                        if action['sid']:
                            self.unlink(action['sid'], pos.get('on_level'))

                            new_level = self.WorldManager.getLevelJSON(target)
                            self.sio.emit(
                                'present level',
                                new_level,
                                room=action['sid']
                            )

                            self.link(action['sid'], target)

                        new_level = self.WorldManager.getLevel(target)

                        pos.setValue('on_level', target)
                        pos.setValue('x', new_level.elements['spawn_tile']['x'])  # noqa
                        pos.setValue('y', new_level.elements['spawn_tile']['y'])  # noqa

                        new_level.addEntity(entity)
                        self.EntityManager.markChanged(entity.id)

                        # Tell players remaining on the level to remove the
                        # player entity of the character who has left.
                        self.emitToLinked(
                            level.id,
                            'remove entity',
                            entity.id
                        )

            elif action['type'] == 'attack':
                self.InteractionManager.attack(
                    action['details']['attacker'],
                    action['details']['defender']
                )

    # Link a client to a level, meaning they will be sent any changes made to
    # the level.
    def link(self, sid, level_id):
        if level_id in self.links:
            self.links[level_id].append(sid)
        else:
            self.links[level_id] = [sid]

    def unlink(self, sid, level_id):
        if level_id in self.links:
            self.links[level_id].remove(sid)

    # Emits a message to the clients linked to the given world ID.
    def emitToLinked(self, level_id, msg, data):
        if level_id in self.links:
            for sid in self.links[level_id]:
                self.sio.emit(msg, data, room=sid)

    # Send out all entity changes to clients.
    def emitUpdates(self):
        changes = self.EntityManager.getChanged()
        self.EntityManager.resetChanged()

        # List of updates to submit to each client.
        to_emit = {}

        for c in changes:
            ent = self.EntityManager.get(c)
            pos = ent.getComp('position')

            if pos:
                level_id = pos.get('on_level')

                if level_id in self.links:
                    for sid in self.links[level_id]:
                        if sid not in to_emit:
                            to_emit[sid] = []

                        to_emit[sid].append(ent.toJSON())

            if ent.deleted:
                self.EntityManager.delete(c)

        # Emit the updates.
        for sid in to_emit:
            self.sio.emit('entity updates', to_emit[sid], room=sid)

    # Creates a new player character entity based on initial details.
    def newCharacter(self, details, sid):
        character = self.EntityManager.new()

        # Give the entity the type "player".
        character.addComponent(self.ComponentManager.new(
            character,
            'type',
            {
                'type': 'player'
            }
        ))

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

        # Give the entity stats.
        character.addComponent(self.ComponentManager.new(
            character,
            'stats',
            {
                'health': 10,
                'attack_damage': 1
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
