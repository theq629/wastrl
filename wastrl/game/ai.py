import tcod
from . import properties as props
from . import events
from . import actions

def make_walk_map(terrain, block_cost=float('inf')):
	walk = tcod.heightmap_new(*terrain.dim)
	for x in range(terrain.dim[0]):
		for y in range(terrain.dim[1]):
			t = terrain[x, y]
			if t in props.walk_over_ap:
				c = props.walk_over_ap[t]
			else:
				c = block_cost
			walk[y, x] = c
	return walk

class Ai:
	__slots__ = (
		'_walk_map',
		'_pather',
		'_taking_turn'
	)

	def __init__(self, terrain):
		self._walk_map = make_walk_map(terrain)
		self._pather = tcod.path.Dijkstra(self._walk_map)
		self._taking_turn = None
		events.take_turn.on.add(self.watch_turn)
		events.move.on.add(self.track_player)

	def watch_turn(self, actor):
		self._taking_turn = actor if actor not in props.is_player else None
		self.take_action(actor)

	def track_player(self, actor, old_pos, new_pos):
		if actor in props.is_player:
			self._pather.set_goal(*new_pos)

	def take_action(self, actor):
		while self._taking_turn == actor:
			actor_pos = props.position[actor]
			path = self._pather.get_path(*actor_pos)
			if len(path) < 2:
				break
			delta = tuple(path[-2][i] - actor_pos[i] for i in range(2))
			action = actions.Move(actor, delta)
			if action.ap is not None and action.ap < props.action_points_this_turn[actor]:
				events.act.trigger(actor, action)
			else:
				break
		if self._taking_turn == actor:
			events.act.trigger(actor, actions.SkipTurn(actor))
