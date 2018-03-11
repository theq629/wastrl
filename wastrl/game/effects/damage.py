import collections
from ... import data
from .. import properties as props
from .. import events
from .. import things
from .. import utils

marker_life = 10

Params = collections.namedtuple('Params', (
	'damage',
	'radius'
))

activates_as = data.ValuedProperty()

_marker_times = data.ValuedProperty()

def make_marker(rng):
	template = dict(things.damage_marker)
	return things.Thing(template)

@events.examine.on.handle(1)
def examine_activatable(thing, detailed):
	if detailed and thing in activates_as:
		params = activates_as[thing]
		dmg_str = "-".join(str(x) for x in params.damage)
		return f"(damage {dmg_str}:{params.radius})"

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		for pos in poses:
			damage = rng.randint(*params.damage)
			target_things = tuple(props.things_at[pos])
			for target_thing in target_things:
				if target_thing != actor:
					events.attack.trigger(actor, target_thing, damage)
			marker = make_marker(rng)
			props.position[marker] = pos
			_marker_times[marker] = marker_life
			events.move.trigger(marker, None, pos)

@events.update.on.handle()
def handle_momentary(rng):
	marker_times = list(_marker_times.items())
	for thing, ticks in marker_times:
		if ticks <= 0:
			events.move.trigger(thing, props.position[thing], None)
			data.BaseProperty.all.remove(thing)
		else:
			_marker_times[thing] -= 1
	return len(marker_times) > 0
