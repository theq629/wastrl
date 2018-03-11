import collections
from ... import data
from .. import properties as props
from .. import events

Params = collections.namedtuple('Params', (
	'amount'
))

activates_as = data.ValuedProperty()

@events.activate.on.handle()
def handle_activation(thing, actor, target_pos, rng):
	if thing in activates_as and actor in props.population:
		params = activates_as[thing]
		props.population[actor] = min(props.population[actor] + params.amount, props.max_population[actor])
