from log import log


# Handles combat and stuff.
class InteractionManager:
    def __init__(self, Manager):
        self.Manager = Manager
        log('InteractionManager', 'Initialized.')

    def attack(self, attacker, defender):
        if attacker.deleted:
            return

        # Set up combat flags.
        if not attacker.combat_status['in_combat']:
            attacker.combat_status['in_combat'] = True
        if not defender.combat_status['in_combat']:
            defender.combat_status['in_combat'] = True

        if defender.id not in attacker.combat_status['with']:
            attacker.combat_status['with'].append(defender.id)
        if attacker.id not in defender.combat_status['with']:
            defender.combat_status['with'].append(attacker.id)

        if attacker.getComp('type').get('type') == 'player' or defender.getComp('type').get('type') == 'player':  # noqa
            attacker.combat_status['human_involved'] = True
            defender.combat_status['human_involved'] = True

        # Calculate damage.
        attacker_damage = attacker.getComp('stats').get('attack_damage')
        defender_health = defender.getComp('stats').get('health')

        defender.getComp('stats').setValue(
            'health',
            defender_health - attacker_damage
        )

        # Check for death.
        killed = False

        if defender.getComp('stats').get('health') <= 0:
            killed = True

            attacker.combat_status['with'].remove(defender.id)
            if len(attacker.combat_status['with']) == 0:
                attacker.combat_status['in_combat'] = False
                attacker.combat_status['human_involved'] = False

            self.Manager.EntityManager.markDeleted(defender.id)

        # Emit details.
        attacker_sid = attacker.getComp('type').get('sid')
        defender_sid = defender.getComp('type').get('sid')

        if attacker.getComp('type').get('type') == 'player':
            self.Manager.sio.emit(
                'combat update',
                attacker.combat_status,
                room=attacker_sid
            )

            self.Manager.sio.emit(
                'player stats',
                attacker.getComp('stats').toJSON(),
                room=attacker_sid
            )

            self.Manager.sio.emit(
                'damage',
                {
                    'type': 'given',
                    'amount': attacker_damage
                },
                room=attacker_sid
            )

        if defender.getComp('type').get('type') == 'player':
            self.Manager.sio.emit(
                'combat update',
                defender.combat_status,
                room=defender_sid
            )

            self.Manager.sio.emit(
                'player stats',
                defender.getComp('stats').toJSON(),
                room=defender_sid
            )

            self.Manager.sio.emit(
                'damage',
                {
                    'type': 'taken',
                    'amount': attacker_damage
                },
                room=defender_sid
            )

        # Log the event.
        attacker_name = attacker.getComp('name').get('name')
        defender_name = defender.getComp('name').get('name')

        msg = f'{attacker_name} did {attacker_damage} damage to {defender_name}'  # noqa
        if killed:
            msg += ' (KILL)'

        log('InteractionManager', msg, 'debug')
