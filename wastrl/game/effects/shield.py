import collections
from ... import data
from .. import properties as props
from .. import things
from .. import events
from .. import utils

Params = collections.namedtuple('Params', (
	'turns'
))

activates_as = data.ValuedProperty()

_shield_turns = data.ValuedProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		_shield_turns[actor] = params.turns

@events.handle_damage.on.handle(0)
def handle_damage(actor, damage):
	if actor in _shield_turns and _shield_turns[actor] > 0:
		return False
	return True

@events.take_turn.on.handle()
def handle_turn(actor):
	if actor in _shield_turns:
		turns = _shield_turns[actor]
		_shield_turns[actor] -= 1
		if turns <= 0:
			_shield_turns.remove(actor)
