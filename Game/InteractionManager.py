from log import log


# Handles combat and stuff.
class InteractionManager:
    def __init__(self, Manager):
        self.Manager = Manager
        log('InteractionManager', 'Initialized.')

    def attack(self, attacker, defender):
        # Set up combat flags.
        attacker.combat_status['in_combat'] = True
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

        # Log the event.
        attacker_name = attacker.getComp('name').get('name')
        defender_name = defender.getComp('name').get('name')

        msg = f'{attacker_name} did {attacker_damage} damage to {defender_name}'  # noqa
        if killed:
            msg += ' (KILL)'

        log('InteractionManager', msg, 'debug')
