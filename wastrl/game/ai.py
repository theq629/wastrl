from . import properties as props
from . import events

class Ai:
	__slots__ = (
		'_is_our_turn'
	)

	def __init__(self):
		self._is_our_turn = False
		events.take_turn.on.add(self.watch_turn)
		'_is_our_turn'

	def watch_turn(self, actor):
		print("ai got turn", actor.index)
		self._is_our_turn = actor not in props.is_player

@events.act.on.handle
def take_player_action(self, thing, available_ap):
	print("AI action", thing.index)
