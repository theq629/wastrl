import math
from . import properties as props

class Move:
	__slots__ = (
		'_actor',
		'_delta',
		'_ap'
	)

	def __init__(self, actor, delta):
		self._actor = actor
		self._delta = delta
		self._ap = self._calc_ap(delta)

	def _calc_ap(self, delta):
		x, y = delta
		return math.sqrt(x**2 + y**2)
	
	@property
	def ap(self):
		return self._ap

	def trigger(self):
		props.position[self._actor] = tuple(props.position[self._actor][i] + self._delta[i] for i in range(2))

class SkipTurn:
	__slots__ = (
		'_ap',
	)

	def __init__(self, actor):
		self._ap = props.action_points_this_turn[actor]
	
	@property
	def ap(self):
		return self._ap

	def trigger(self):
		pass
