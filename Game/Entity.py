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

        self.combat_status = {
            'in_combat': False,
            'with': [],
            'human_involved': False
        }

        log(f'Entity#{self.id}', 'Created.', 'debug(2)')

    # If the entity is a mob, this updates them (movement, etc.)
    def updateMob(self, WorldManager, force_move=False):
        if self.deleted:
            return

        if self.combat_status['in_combat'] and self.combat_status['human_involved'] and not force_move:  # noqa
            return

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
                    res = WorldManager.validMove(self.getComp('position').get('on_level'), a)  # noqa

                    if res == 'valid':
                        possible_spots.append(a)
                    elif isinstance(res, Entity):
                        if self.getComp('ai'):
                            aggression = self.getComp('ai').get('aggression')

                            # If this entity is not aggressive, let it move
                            # onto the tile of another entity.
                            if aggression == 'none':
                                possible_spots.append(a)

                            # If this entity IS aggressive, have it attack when
                            # it moves onto another entity.
                            elif aggression == 'passive-aggressive':
                                # But disallow attack if the target is already
                                # in combat.
                                if (not res.combat_status['in_combat']) or (res.id in self.combat_status['with']):  # noqa
                                    if (res.getComp('type').get('type') == 'player') or self.getComp('ai').get('attacks_mobs'):  # noqa
                                        a['attacking'] = res
                                        possible_spots.append(a)

                if len(possible_spots):
                    move_to = possible_spots[random.randint(
                        0,
                        len(possible_spots) - 1
                    )]

                    if 'attacking' in move_to:
                        WorldManager.Manager.queueAction(
                            0,
                            'attack',
                            {
                                'attacker': self,
                                'defender': move_to['attacking']
                            }
                        )

                    else:
                        WorldManager.Manager.queueAction(
                            0,
                            'move',
                            {
                                'entity': self.id,
                                'coord': move_to
                            }
                        )

    # Adds a component to the entity. Only one component of each type can
    # exist.
    def addComponent(self, component):
        self.components[component.type] = component

        log(
            f'Entity#{self.id}',
            f'Component of type {component.type} added.',
            'debug(2)'
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
