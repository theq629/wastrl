import collections
from ... import data
from .. import properties as props
from .. import things
from .. import events
from .. import utils

damage_range = (3, 10)

Params = collections.namedtuple('Params', (
	'radius'
))

activates_as = data.ValuedProperty()

_gas_density = data.ValuedProperty()

def move_gas(pos, density, rng):
	u = rng.uniform(0, 1)
	if u < 4 / density:
		return pos[0], pos[1] + 1
	elif u < 8 / density:
		return pos[0] + rng.randint(-1, 1), pos[1] + 1
	else:
		return pos[0] + rng.randint(-1, 1), pos[1] + rng.randint(-1, 1)

def make_gas(rng):
	template = dict(things.gas)
	min_colour_value = 196
	max_colour_value = 128
	colour = (rng.randint(min_colour_value, max_colour_value), rng.randint(min_colour_value, max_colour_value), rng.randint(min_colour_value, max_colour_value))
	template[props.graphics] = template[props.graphics]._replace(colour=colour)
	return things.Thing(template)

def start(points, rng):
	for pos in points:
		gas = make_gas(rng)
		props.position[gas] = pos
		_gas_density[gas] = rng.randint(5, 10)
		events.move.trigger(gas, None, pos)

@events.examine.on.handle(1)
def examine_activatable(thing, detailed):
	if detailed and thing in activates_as:
		params = activates_as[thing]
		return f"(gas :{params.radius})"

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		start(poses, rng)

@events.start_turn.on.handle()
def handle_turn(rng):
	gas_densities = list(_gas_density.items())

	for thing, density in gas_densities:
		if density <= 0:
			events.move.trigger(thing, props.position[thing], None)
			data.BaseProperty.all.remove(thing)
		elif rng.uniform(0, 1) < 0.5:
			_gas_density[thing] -= 1
			if density > 1:
				pos = props.position[thing]
				for other_thing in tuple(t for t in props.things_at[pos] if t in props.is_alive):
					events.take_damage.trigger(other_thing, rng.randint(*damage_range))
				new_pos = move_gas(pos, density, rng)
				if not any(t in _gas_density for t in props.things_at[new_pos]):
					new_gas = make_gas(rng)
					props.position[new_gas] = new_pos
					_gas_density[new_gas] = density - 1
					events.move.trigger(new_gas, None, new_pos)
	
	return len(gas_densities) > 0
