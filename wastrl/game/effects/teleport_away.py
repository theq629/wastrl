import collections
from ... import data
from .. import properties as props
from .. import events

teleport_range = 20

activates_as = data.SetProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		things_there = tuple(props.things_at[target_pos])
		alive_things_there = tuple(t for t in things_there if t in props.is_alive)
		if len(alive_things_there) > 0:
			to_teleport = alive_things_there
		else:
			to_teleport = things_there

		to_teleport = to_teleport[rng.randint(0, len(to_teleport) - 1)]

		new_pos = None
		while True:
			new_pos = tuple(target_pos[i] + rng.randint(-teleport_range, teleport_range) for i in range(2))
			if new_pos in props.things_at:
				break

		props.position[to_teleport] = new_pos
		events.move.trigger(to_teleport, target_pos, new_pos)
