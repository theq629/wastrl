from ... import data
from .. import properties as props
from .. import things
from .. import events

_updates_to_live = 1

_momentary = data.ValuedProperty()

def explode(points):
	for pos in points:
		explosion = things.explosion()
		props.position[explosion] = pos
		_momentary[explosion] = _updates_to_live

@events.update.on.handle()
def handle_momentary():
	things = list(_momentary.items())
	for thing, ticks in things:
		if ticks <= 0:
			data.BaseProperty.all.remove(thing)
		else:
			_momentary[thing] -= 1
	return len(things) > 0
