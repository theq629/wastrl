import collections
from ... import data
from .. import properties as props
from .. import events
from .. import things
from .. import utils

mountain_prob = 0.75

Params = collections.namedtuple('Params', (
	'radius'
))

activates_as = data.ValuedProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		for pos in poses:
			if pos in props.terrain_at:
				if rng.uniform(0, 1) < mountain_prob:
					props.terrain_at[pos] = things.mountains
					events.terrain_change.trigger(pos)
