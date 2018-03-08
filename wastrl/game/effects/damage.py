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
		damage = rng.randint(*params.damage)
		poses = tuple(utils.iter_radius(target_pos, params.radius))
		explosion.explode(poses)
		for pos in poses:
			for target_thing in props.things_at[pos]:
				events.attack.trigger(actor, target_thing, damage)
