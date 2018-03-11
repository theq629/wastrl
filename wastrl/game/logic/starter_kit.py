from .. import properties as props
from .. import events

@events.examine.on.handle(30)
def examine(thing, detailed):
	if detailed and thing in props.is_from_starter_kit:
		return f"(starter kit)"
