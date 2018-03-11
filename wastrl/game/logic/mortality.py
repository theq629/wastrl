from .. import properties as props
from .. import events

@events.attack.on.handle(1000)
def handle_damage(attackee, target, damage):
	if target in props.is_alive:
		events.send_damage.trigger(target, damage)

@events.send_damage.on.handle()
def handle_get_damage(target, damage):
	props.population[target] -= damage
	events.take_damage.trigger(target, damage)

@events.take_damage.on.handle(1000)
def handle_death(thing, damage):
	if props.population[thing] <= 0:
		pos = props.position[thing]
		props.population[thing] = 0
		props.is_alive.remove(thing)
		props.is_dead.add(thing)
		props.action_points.remove(thing)
		props.action_points_this_turn.remove(thing)
		props.position.remove(thing)
		events.move.trigger(thing, pos, None)
		events.die.trigger(thing)
