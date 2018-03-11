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

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as and actor in props.fov:
		params = activates_as[thing]
		for pos in utils.iter_radius(target_pos, params.radius):
			props.fov[actor].add(pos)
			props.seen_fov[actor].add(pos)
