import numpy
import tcod
from .. import data
from . import tilemap
from . import properties as props
from . import events
from . import actions
from . import utils

ai_activation_range = 40
guard_wakeup_range = 4

out_of_range_value = float('inf')
guard_wakeup_range_2 = guard_wakeup_range**2

_actor_goal = data.ValuedProperty()
_actor_path = data.ValuedProperty()

class DijkstraMap:
	__slots__ = (
		'terrain',
		'max_dist_to_player',
		'_walk_map',
		'_map',
		'_goal'
	)

	def __init__(self, terrain, max_dist_to_player=ai_activation_range):
		self.terrain = terrain
		self.max_dist_to_player = max_dist_to_player
		self._walk_map = self.make_walk_map(terrain)
		self._map = numpy.zeros(shape=tuple(reversed(self.terrain.dim)))
		self._goal = None

	def make_walk_map(self, terrain, block_cost=float('inf')):
		walk = numpy.zeros(shape=tuple(reversed(terrain.dim)))
		for x in range(terrain.dim[0]):
			for y in range(terrain.dim[1]):
				t = terrain[x, y]
				if t in props.walk_over_ap:
					c = props.walk_over_ap[t]
				else:
					c = block_cost
				walk[y, x] = c
		return walk

	def update(self, player_pos):
		self._goal = player_pos
		self._map[:] = out_of_range_value
		fringe = tilemap.SearchFringe()
		fringe.put(player_pos, 0)
		while not fringe.is_empty():
			node = fringe.pop()
			node_dist = fringe.get(node)
			x, y = node
			self._map[y, x] = node_dist
			for neighbour in tilemap.neighbours(node):
				x, y = neighbour
				if x >= 0 and y >= 0 and x < self._walk_map.shape[1] and y < self._walk_map.shape[0]:
					new_dist = node_dist + self._walk_map[y, x]
					if new_dist <= self.max_dist_to_player:
						old_dist = fringe.get(neighbour)
						if old_dist is None or new_dist < old_dist:
							fringe.put(neighbour, new_dist)

	def _trace_path(self, pos):
		node = pos
		while node != self._goal:
			yield node
			node = min(self.terrain.neighbours(node), key=lambda p: self._map[p[1], p[0]])
		yield node

	def get_path(self, pos):
		if self._goal is None:
			return None
		x, y = pos
		if self._map[y, x] == out_of_range_value:
			return None
		return self._trace_path(pos)

class Ai:
	__slots__ = (
		'_rng',
		'_dijkstra_map',
		'_taking_turn',
		'_player_pos'
	)

	def __init__(self, rng, terrain):
		self._rng = rng
		self._dijkstra_map = DijkstraMap(terrain)
		self._taking_turn = None
		self._player_pos = None
		events.take_turn.on.add(self.watch_turn)
		events.move.on.add(self.track_player)
		events.die.on.add(self.track_player_death)

	def watch_turn(self, actor):
		self._taking_turn = actor if actor not in props.is_player else None
		self.take_action(actor)

	def track_player(self, actor, old_pos, new_pos):
		if actor in props.is_player:
			if actor in props.is_alive:
				self._dijkstra_map.update(new_pos)
				self._player_pos = new_pos
				for guard in tuple(props.is_guarding_city):
					guard_pos = props.position[guard]
					if sum((self._player_pos[i] - guard_pos[i])**2 for i in range(2)) < guard_wakeup_range_2:
						props.is_guarding_city.remove(guard)
						events.guard_wakeup.trigger(guard)
			else:
				self._player_pos = None

	def track_player_death(self, actor):
		if actor in props.is_player:
			self._player_pos = None

	def update_goals(self, actor, can_see_player):
		actor_pos = props.position[actor]
		if (actor not in _actor_goal or _actor_goal[actor] != self._player_pos) and can_see_player:
			_actor_goal[actor] = self._player_pos
			path = self._dijkstra_map.get_path(actor_pos)
			if path is not None:
				path = tuple(path)[1:]
				_actor_path[actor] = path
			elif actor in _actor_path:
				_actor_path.remove(actor)

	def custom_path(self, actor_pos, goal_pos):
		def cost(from_pos, pos):
			t = self._dijkstra_map.terrain[pos]
			if t not in props.walk_over_ap:
				return utils.blocked_cost
			elif props.blocked_at[pos] and pos != goal_pos:
				return utils.blocked_cost
			else:
				return props.walk_over_ap[t]
		path = tilemap.pathfind(
			graph = self._dijkstra_map.terrain,
			starts = (actor_pos,),
			goal = goal_pos,
			cost = cost,
			max_dist = self._dijkstra_map.max_dist_to_player / 2
		)
		if path is not None:
			path = tuple(path)[1:]
		return path

	def try_action(self, actor):
		if actor in props.is_guarding_city:
			return

		actor_pos = props.position[actor]
		can_see_player = self.can_see(actor_pos, self._player_pos)

		self.update_goals(actor, can_see_player)

		while self._taking_turn == actor and self._player_pos is not None:
			actor_pos = props.position[actor]

			if can_see_player and actor in props.intrinsics:
				can_use = tuple(props.intrinsics[actor]) + tuple(props.inventory[actor])
				num_can_use = len(can_use)
				if num_can_use > 0:
					to_use = can_use[self._rng.randint(0, num_can_use - 1)]
					action = actions.Activate(actor, to_use, self._player_pos)
					if action.ap is not None and action.ap < props.action_points_this_turn[actor]:
						events.act.trigger(actor, action)

			if actor not in _actor_path:
				break
			path = _actor_path[actor]
			if len(path) == 0:
				break
			next_pos = path[0]
			delta = tuple(next_pos[i] - actor_pos[i] for i in range(2))

			if props.blocked_at[next_pos] and actor in _actor_goal:
				path = self.custom_path(actor_pos, _actor_goal[actor])
				if path is None:
					_actor_path.remove(actor)
					break
				_actor_path[actor] = path
				if len(path) == 0:
					break
				delta = tuple(path[0][i] - actor_pos[i] for i in range(2))

			action = actions.Move(actor, delta)
			if action.ap is not None and action.ap < props.action_points_this_turn[actor]:
				_actor_path[actor] = path[1:]
				events.act.trigger(actor, action)
			else:
				break

	def take_action(self, actor):
		try:
			if self._player_pos is not None:
				self.try_action(actor)
		finally:
			if self._taking_turn == actor:
				events.act.trigger(actor, actions.SkipTurn(actor))

	def can_see(self, actor_pos, target_pos):
		for pos in tcod.line_iter(actor_pos[0], actor_pos[1], target_pos[0], target_pos[1]):
			if any(t in props.blocks_vision for t in props.things_at[pos]):
				return False
		return True
