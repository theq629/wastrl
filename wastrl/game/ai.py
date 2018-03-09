import numpy
from . import tilemap
from . import properties as props
from . import events
from . import actions
from . import utils

out_of_range_value = float('inf')

class DijkstraMap:
	__slots__ = (
		'_terrain',
		'_max_dist_to_player',
		'_map'
	)

	def __init__(self, terrain, max_dist_to_player=50):
		self._terrain = terrain
		self._max_dist_to_player = max_dist_to_player
		self._map = numpy.zeros(shape=tuple(reversed(self._terrain.dim)))

	def update(self, player_pos):
		self._map[:] = out_of_range_value
		def touch(pos, dist):
			if dist > self._max_dist_to_player:
				return False
			else:
				x, y = pos
				self._map[y, x] = dist
				return True
		start_time = time.time()
		tilemap.dijkstra(
			graph = self._terrain,
			starts = (player_pos,),
			touch = touch,
			cost = utils.walk_cost(self._terrain)
		)

	def move_from(self, pos):
		x, y = pos
		if self._map[y, x] == out_of_range_value:
			return None
		pos1 = min(self._terrain.neighbours(pos), key=lambda p: self._map[p[1], p[0]])
		return tuple(pos1[i] - pos[i] for i in range(2))

class Ai:
	__slots__ = (
		'_dijkstra_map',
		'_taking_turn'
	)

	def __init__(self, terrain):
		self._dijkstra_map = DijkstraMap(terrain)
		self._taking_turn = None
		events.take_turn.on.add(self.watch_turn)
		events.move.on.add(self.track_player)

	def watch_turn(self, actor):
		self._taking_turn = actor if actor not in props.is_player else None
		self.take_action(actor)

	def track_player(self, actor, old_pos, new_pos):
		if actor in props.is_player:
			self._dijkstra_map.update(new_pos)

	def take_action(self, actor):
		while self._taking_turn == actor:
			actor_pos = props.position[actor]
			delta = self._dijkstra_map.move_from(actor_pos)
			if delta is None:
				break
			action = actions.Move(actor, delta)
			if action.ap is not None and action.ap < props.action_points_this_turn[actor]:
				events.act.trigger(actor, action)
			else:
				break
		if self._taking_turn == actor:
			events.act.trigger(actor, actions.SkipTurn(actor))
