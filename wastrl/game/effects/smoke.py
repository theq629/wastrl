import collections
from ... import data
from .. import properties as props
from .. import things
from .. import events
from .. import utils

Params = collections.namedtuple('Params', (
	'radius'
))

activates_as = data.ValuedProperty()

_smoke_density = data.ValuedProperty()

def move_smoke(pos, density, rng):
	u = rng.uniform(0, 1)
	if u < 8 / density:
		return pos[0], pos[1] + 1
	elif u < 18 / density:
		return pos[0] + rng.randint(-1, 1), pos[1] + 1
	else:
		return pos[0] + rng.randint(-1, 1), pos[1] + rng.randint(-1, 1)

def make_smoke(rng):
	template = dict(things.smoke)
	min_colour_value = 200
	colour = (rng.randint(min_colour_value, 255), rng.randint(min_colour_value, 255), rng.randint(min_colour_value, 255))
	template[props.graphics] = template[props.graphics]._replace(colour=colour)
	return things.Thing(template)

def start(points, rng):
	for pos in points:
		smoke = make_smoke(rng)
		props.position[smoke] = pos
		_smoke_density[smoke] = rng.randint(5, 10)
		events.move.trigger(smoke, None, pos)

@events.examine.on.handle(1)
def examine_activatable(thing, detailed):
	if detailed and thing in activates_as:
		params = activates_as[thing]
		return f"(smoke :{params.radius})"

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		start(poses, rng)

@events.start_turn.on.handle()
def handle_turn(rng):
	smoke_densities = list(_smoke_density.items())

	for thing, density in smoke_densities:
		if density <= 0:
			data.BaseProperty.all.remove(thing)
		elif rng.uniform(0, 1) < 0.5:
			_smoke_density[thing] -= 1
			if density > 1:
				pos = props.position[thing]
				new_pos = move_smoke(pos, density, rng)
				if not any(t in _smoke_density for t in props.things_at[new_pos]):
					new_smoke = make_smoke(rng)
					props.position[new_smoke] = new_pos
					_smoke_density[new_smoke] = density - 1
					events.move.trigger(thing, None, new_pos)
	
	return len(smoke_densities) > 0
