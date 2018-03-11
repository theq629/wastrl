import tcod
import collections
from ... import data
from .. import properties as props
from .. import events
from .. import things

activates_as = data.SetProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		actor_pos = props.position[actor]
		for pos in tcod.line_iter(actor_pos[0], actor_pos[1], target_pos[0], target_pos[1]):
			if pos in props.terrain_at:
				t = props.terrain_at[pos]
				if t == things.mountains:
					props.terrain_at[pos] = things.desert
					events.terrain_change.trigger(pos)
