from . import properties as props
from . import events

class Base:
	__slots__ = (
		'_ap',
	)

	def __init__(self):
		self._ap = self._calc_ap()
	
	@property
	def ap(self):
		return self._ap

	def trigger(self):
		pass

class SkipTurn(Base):
	__slots__ = (
		'_actor'
	)

	def __init__(self, actor):
		self._actor = actor
		super().__init__()

	def _calc_ap(self):
		return props.action_points_this_turn[self._actor]

class Move(Base):
	__slots__ = (
		'_actor',
		'_delta'
	)

	def __init__(self, actor, delta):
		self._actor = actor
		self._delta = delta
		super().__init__()

	def _calc_ap(self):
		dx, dy = self._delta
		if abs(dx) > 1 or abs(dy) > 1 or abs(dx) + abs(dy) == 0:
			return None
		x, y = props.position[self._actor]
		x, y = x + dx, y + dy
		t = props.terrain_at[x, y]
		try:
			return props.walk_over_ap[t]
		except KeyError:
			return None

	def trigger(self):
		old_pos = props.position[self._actor]
		new_pos = tuple(old_pos[i] + self._delta[i] for i in range(2))
		props.position[self._actor] = new_pos
		events.move.trigger(self._actor, old_pos, new_pos)

class Get(Base):
	__slots__ = (
		'_actor',
		'_things'
	)

	def __init__(self, actor, things):
		self._actor = actor
		self._things = things
		super().__init__()

	def _calc_ap(self):
		if self._actor in props.inventory and all(t in props.position and props.position[t] == props.position[self._actor] for t in self._things):
			return 1
		else:
			return None

	def trigger(self):
		pos = props.position[self._actor]
		for thing in self._things:
			props.position.remove(thing)
			props.inventory[self._actor].add(thing)
			events.move.trigger(thing, pos, None)
			events.get.trigger(self._actor, thing)

class Drop(Base):
	__slots__ = (
		'_actor',
		'_things'
	)

	def __init__(self, actor, things):
		self._actor = actor
		self._things = things
		super().__init__()

	def _calc_ap(self):
		if self._actor in props.inventory and all(t in props.inventory[self._actor] for t in self._things):
			return 1
		else:
			return None

	def trigger(self):
		pos = props.position[self._actor]
		for thing in self._things:
			props.inventory[self._actor].remove(thing)
			props.position[thing] = pos
			events.drop.trigger(self._actor, thing)
			events.move.trigger(thing, None, pos)

class Attack(Base):
	__slots__ = (
		'_actor',
		'_target'
	)

	def __init__(self, actor, target):
		self._actor = actor
		self._target = target
		super.__init__()

	def trigger(self):
		props.population[self._target] = max(0, pops.population[self._target] - 5)
		if props.population[self._target] <= 0:
			event.die.trigger(self._target)
