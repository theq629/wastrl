from .. import properties as props
from .. import events
from .. import utils

@events.activate.on.handle(10)
def handle_activation(thing, actor, target_pos, rng):
	if thing in props.single_use:
		utils.unspawn(thing)
