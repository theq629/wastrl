import collections
from ... import data
from .. import properties as props
from .. import events
from .. import utils
from . import explosion

Params = collections.namedtuple('Params', (
	'damage'
))

activates_as = data.ValuedProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as:
		params = activates_as[thing]
		damage = rng.randint(*params.damage)
		target_things = tuple(props.things_at[target_pos])
		for target_thing in target_things:
			events.attack.trigger(actor, target_thing, damage)
