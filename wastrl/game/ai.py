import numpy
import tcod
from .. import data
from . import tilemap
from . import properties as props
from . import events
from . import actions
from . import utils

out_of_range_value = float('inf')

_actor_goal = data.ValuedProperty()
_actor_path = data.ValuedProperty()

class DijkstraMap:
	__slots__ = (
		'_terrain',
		'_max_dist_to_player',
		'_walk_map',
		'_map',
		'_goal'
	)

	def __init__(self, terrain, max_dist_to_player=40):
		self._terrain = terrain
		self._max_dist_to_player = max_dist_to_player
		self._walk_map = self.make_walk_map(terrain)
		self._map = numpy.zeros(shape=tuple(reversed(self._terrain.dim)))
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
					if new_dist <= self._max_dist_to_player:
						old_dist = fringe.get(neighbour)
						if old_dist is None or new_dist < old_dist:
							fringe.put(neighbour, new_dist)

	def _trace_path(self, pos):
		node = pos
		while node != self._goal:
			yield node
			node = min(self._terrain.neighbours(node), key=lambda p: self._map[p[1], p[0]])
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
		'_dijkstra_map',
		'_taking_turn',
		'_player_pos'
	)

	def __init__(self, terrain):
		self._dijkstra_map = DijkstraMap(terrain)
		self._taking_turn = None
		self._player_pos = None
		events.take_turn.on.add(self.watch_turn)
		events.move.on.add(self.track_player)

	def watch_turn(self, actor):
		self._taking_turn = actor if actor not in props.is_player else None
		self.take_action(actor)

	def track_player(self, actor, old_pos, new_pos):
		if actor in props.is_player:
			self._dijkstra_map.update(new_pos)
			self._player_pos = new_pos

	def update_goals(self, actor):
		actor_pos = props.position[actor]
		if (actor not in _actor_goal or _actor_goal[actor] != self._player_pos) and self.can_see(actor_pos, self._player_pos):
			_actor_goal[actor] = self._player_pos
			path = self._dijkstra_map.get_path(actor_pos)
			if path is not None:
				path = tuple(path)[1:]
				_actor_path[actor] = path
			elif actor in _actor_path:
				_actor_path.remove(actor)

	def take_action(self, actor):
		self.update_goals(actor)
		while self._taking_turn == actor:
			actor_pos = props.position[actor]
			if actor not in _actor_path:
				break
			path = _actor_path[actor]
			if len(path) == 0:
				break
			delta = tuple(path[0][i] - actor_pos[i] for i in range(2))
			action = actions.Move(actor, delta)
			if action.ap is not None and action.ap < props.action_points_this_turn[actor]:
				_actor_path[actor] = path[1:]
				events.act.trigger(actor, action)
			else:
				break
		if self._taking_turn == actor:
			events.act.trigger(actor, actions.SkipTurn(actor))

	def can_see(self, actor_pos, target_pos):
		for pos in tcod.line_iter(actor_pos[0], actor_pos[1], target_pos[0], target_pos[1]):
			if any(t in props.blocks_vision for t in props.things_at[pos]):
				return False
		return True
