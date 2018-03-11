import collections
from ... import data
from .. import properties as props
from .. import things
from .. import events
from .. import utils
from . import smoke as effect_smoke

damage_range = (3, 10)
burn_down_prob = 0.9
spread_prob = 0.75
go_out_prob = 0.1
smoke_prob = 0.1

Params = collections.namedtuple('Params', (
	'radius'
))

activates_as = data.ValuedProperty()

_fire = data.ValuedProperty()

def make_fire(rng):
	template = dict(things.fire)
	min_colour_value = 200
	colour = (rng.randint(min_colour_value, 255), 0, 0)
	template[props.graphics] = template[props.graphics]._replace(colour=colour)
	return things.Thing(template)

def start(points, rng, strength=3):
	for pos in points:
		fire = make_fire(rng)
		props.position[fire] = pos
		_fire[fire] = rng.randint(1, strength)
		events.move.trigger(fire, None, pos)

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		start(poses, rng)

@events.start_turn.on.handle(1)
def handle_turn(rng):
	fires = tuple(_fire.items())
	for fire, strength in fires:
		pos = props.position[fire]
		go_out = False
		if any(t in props.suppresses_fire for t in props.things_at[pos]):
			go_out = True
		else:
			for thing in tuple(t for t in props.things_at[pos] if t in props.is_alive):
				events.take_damage.trigger(thing, rng.randint(*damage_range))
			if rng.uniform(0, 1) < burn_down_prob:
				props.terrain_at[pos] = things.desert
			if rng.uniform(0, 1) < smoke_prob:
				effect_smoke.start((pos,), rng)
			if rng.uniform(0, 1) < spread_prob:
				new_pos = pos[0] + rng.randint(-1, 1), pos[1] + rng.randint(-1, 1)
				if props.terrain_at[new_pos] in props.is_flamable and not any(t in _fire for t in props.things_at[new_pos]):
					new_fire = make_fire(rng)
					props.position[new_fire] = new_pos
					_fire[new_fire] = rng.randint(1, strength)
					events.move.trigger(new_fire, None, new_pos)
			if rng.uniform(0, 1) < go_out_prob:
				go_out = True
		if go_out:
			_fire.remove(fire)
			events.move.trigger(fire, props.position[fire], None)
			props.position.remove(fire)
