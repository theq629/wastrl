from .. import properties as props
from .. import events
from .. import utils

fov_range = 20

@events.move.on.handle()
def update_fov(actor, move_from, move_to):
	if actor in props.fov:
		pos = props.position[actor]
		move_range, see_range = utils.get_ranges((pos,), props.action_points[actor], fov_range)
		props.fov[actor] = see_range
		props.seen_fov[actor].update(see_range)
