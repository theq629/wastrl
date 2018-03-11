import collections
from ... import data
from .. import properties as props
from .. import things
from .. import events
from .. import utils
from . import smoke as effect_smoke
from . import fire as effect_fire

Params = collections.namedtuple('Params', (
	'damage',
	'radius'
))

chance_of_smoke = 0.25
chance_of_fire = 0.01
chance_of_fire_on_flamable = 0.1

activates_as = data.ValuedProperty()

_explosion_times = data.ValuedProperty()
_smoke_times = data.ValuedProperty()

def make_explosion(rng):
	template = dict(things.explosion)
	colour = (rng.randint(128, 255), 0, 0)
	template[props.graphics] = template[props.graphics]._replace(colour=colour)
	return things.Thing(template)

def make_explosion_smoke(rng):
	template = dict(things.explosion_smoke)
	min_colour_value = 196
	colour = (rng.randint(min_colour_value, 255), rng.randint(min_colour_value, 255), rng.randint(min_colour_value, 255))
	template[props.graphics] = template[props.graphics]._replace(colour=colour)
	return things.Thing(template)

def explode(points, rng):
	for pos in points:
		u = rng.uniform(0, 1)
		if u < chance_of_fire:
			effect_fire.start((pos,), rng)
		elif u < chance_of_fire_on_flamable and props.terrain_at[pos] in props.is_flamable:
			effect_fire.start((pos,), rng)
		if rng.uniform(0, 1) < chance_of_smoke:
			effect_smoke.start((pos,), rng)
		explosion = make_explosion(rng)
		props.position[explosion] = pos
		_explosion_times[explosion] = rng.randint(2, 3)
		events.move.trigger(explosion, None, pos)

@events.examine.on.handle(1)
def examine_activatable(thing, detailed):
	if detailed and thing in activates_as:
		params = activates_as[thing]
		dmg_str = "-".join(str(x) for x in params.damage)
		return f"(explosion {dmg_str}:{params.radius})"

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		damage = rng.randint(*params.damage)
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		explode(poses, rng)
		for pos in poses:
			target_things = tuple(props.things_at[pos])
			for target_thing in target_things:
				events.attack.trigger(actor, target_thing, damage)

@events.update.on.handle()
def handle_momentary(rng):
	explosion_times = list(_explosion_times.items())
	smoke_times = list(_smoke_times.items())

	for thing, ticks in explosion_times:
		if ticks <= 0:
			pos = props.position[thing]
			smoke = make_explosion_smoke(rng)
			props.position[smoke] = pos
			_smoke_times[smoke] = rng.randint(2, 4)
			events.move.trigger(thing, pos, None)
			events.move.trigger(smoke, None, pos)
			data.BaseProperty.all.remove(thing)
		else:
			_explosion_times[thing] -= 1

	for thing, ticks in smoke_times:
		if ticks <= 0:
			events.move.trigger(thing, props.position[thing], None)
			data.BaseProperty.all.remove(thing)
		else:
			_smoke_times[thing] -= 1

	return len(explosion_times) + len(smoke_times) > 0
