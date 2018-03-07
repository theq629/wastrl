from . import properties as props
from . import events

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
		dx, dy = delta
		x, y = props.position[self._actor]
		x, y = x + dx, y + dy
		t = props.terrain_at[x, y]
		try:
			return props.walk_over_ap[t]
		except KeyError:
			return None
	
	@property
	def ap(self):
		return self._ap

	def trigger(self):
		old_pos = props.position[self._actor]
		new_pos = tuple(old_pos[i] + self._delta[i] for i in range(2))
		props.position[self._actor] = new_pos
		events.move.trigger(self._actor, old_pos, new_pos)

class Attack:
	__slots__ = (
		'_actor',
		'_target',
		'_ap'
	)

	def __init__(self, actor, target):
		self._actor = actor
		self._target = target
		self._ap = self._calc_ap()

	def _calc_ap(self):
		return 1

	@property
	def ap(self):
		return self._ap

	def trigger(self):
		props.population[self._target] = max(0, pops.population[self._target] - 5)
		if props.population[self._target] <= 0:
			event.die.trigger(self._target)

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
