import collections
from ... import data
from .. import properties as props
from .. import events

activates_as = data.SetProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		if target_pos not in props.things_at:
			return
		pos = props.position[actor]
		props.position[actor] = target_pos
		events.move.trigger(actor, pos, target_pos)
