import collections
from ... import data
from .. import properties as props
from .. import events
from .. import utils
from . import explosion

Params = collections.namedtuple('Params', (
	'damage',
	'radius'
))

activates_as = data.ValuedProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		for pos in poses:
			damage = rng.randint(*params.damage)
			target_things = tuple(props.things_at[pos])
			for target_thing in target_things:
				if target_things != actor:
					events.attack.trigger(actor, target_thing, damage)
