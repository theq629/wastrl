from ... import data
from .. import properties as props
from .. import things
from .. import events
from . import smoke as effect_smoke

chance_of_smoke = 0.25

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
		if rng.uniform(0, 1) < chance_of_smoke:
			effect_smoke.start((pos,), rng)
		explosion = make_explosion(rng)
		props.position[explosion] = pos
		_explosion_times[explosion] = rng.randint(2, 3)

@events.update.on.handle()
def handle_momentary(rng):
	explosion_times = list(_explosion_times.items())
	smoke_times = list(_smoke_times.items())

	for thing, ticks in explosion_times:
		if ticks <= 0:
			smoke = make_explosion_smoke(rng)
			props.position[smoke] = props.position[thing]
			_smoke_times[smoke] = rng.randint(2, 4)
			data.BaseProperty.all.remove(thing)
		else:
			_explosion_times[thing] -= 1

	for thing, ticks in smoke_times:
		if ticks <= 0:
			data.BaseProperty.all.remove(thing)
		else:
			_smoke_times[thing] -= 1

	return len(explosion_times) + len(smoke_times) > 0
