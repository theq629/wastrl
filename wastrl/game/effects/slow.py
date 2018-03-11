import collections
from ... import data
from .. import properties as props
from .. import events

Params = collections.namedtuple('Params', (
	'amount',
	'turns'
))

activates_as = data.ValuedProperty()

_turns = data.ValuedProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as and actor in props.action_points:
		params = activates_as[thing]
		for target in tuple(t for t in props.things_at[target_pos] if t in props.action_points):
			_turns[target] = (params.turns, int(props.action_points[target] * params.amount))

@events.take_turn.on.handle(-1)
def handle_turn(actor):
	if actor in _turns:
		turns, amount = _turns[actor]
		turns -= 1
		props.action_points_this_turn[actor] -= amount
		if turns <= 0:
			_turns.remove(actor)
		else:
			_turns[actor] = (turns, amount)
