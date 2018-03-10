from . import properties as props
from . import events
from . import tilemap
from . import utils

min_terrain_cost = 0.5

class Base:
	__slots__ = (
		'_ap',
	)

	def __init__(self):
		self._ap = self._calc_ap()
	
	@property
	def ap(self):
		return self._ap

	def trigger(self, rng):
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
		if (x, y) not in props.things_at:
			return None
		try:
			if any(t in props.is_blocking for t in props.things_at[x, y]):
				return None
		except KeyError:
			return None
		t = props.terrain_at[x, y]
		try:
			return props.walk_over_ap[t]
		except KeyError:
			return None

	def trigger(self, rng):
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

	def trigger(self, rng):
		for thing in self._things:
			pos = props.position[thing]
			props.position.remove(thing)
			props.inventory[self._actor].add(thing)
			events.get.trigger(self._actor, thing)
			events.move.trigger(thing, pos, None)

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

	def trigger(self, rng):
		pos = props.position[self._actor]
		for thing in self._things:
			props.inventory[self._actor].remove(thing)
			props.position[thing] = pos
			events.drop.trigger(self._actor, thing)
			events.move.trigger(thing, None, pos)

class Activate(Base):
	__slots__ = (
		'_actor',
		'_thing',
		'_target_pos'
	)

	def __init__(self, actor, thing, target_pos):
		self._actor = actor
		self._thing = thing
		self._target_pos = target_pos
		super().__init__()

	def _is_valid(self):
		actor_pos = props.position[self._actor]
		act_range = props.activation_target_range[self._thing]
		fire_range_2 = act_range.fire_range**2

		if sum((actor_pos[i] - self._target_pos[i])**2 for i in range(2)) > (act_range.move_range / min_terrain_cost + act_range.fire_range)**2:
			return False

		move_points = set()
		def touch(pos, dist):
			move_points.add(pos)
			return True
		tilemap.dijkstra(
			starts = (actor_pos,),
			touch = touch,
			cost = utils.walk_cost_prop,
			max_dist = act_range.move_range
		)

		for point in move_points:
			r = sum((point[i] - self._target_pos[i])**2 for i in range(2))
			if r <= fire_range_2:
				return True
		return False

	def _calc_ap(self):
		if self._is_valid():
			return 1
		else:
			return None

	def trigger(self, rng):
		events.activate.trigger(self._thing, self._actor, self._target_pos, rng)
