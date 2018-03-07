from . import properties as props
from . import events

def spawn(thing, pos):
	props.position[thing] = pos
	events.move.trigger(thing, None, pos)
