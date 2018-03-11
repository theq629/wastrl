import collections
from ... import data
from .. import properties as props
from .. import events

Params = collections.namedtuple('Params', (
	'amount'
))

activates_as = data.ValuedProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as and actor in props.action_points:
		params = activates_as[thing]
		add_ap = int(props.action_points[actor] * params.amount)
		props.action_points_this_turn[actor] += add_ap
