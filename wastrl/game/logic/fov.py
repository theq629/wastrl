import tcod, tcod.map
from ... import data
from .. import properties as props
from .. import events
from .. import utils

fov_range = 35

class Fover:
	__slots__ = (
		'_player',
		'_dim',
		'_map',
		'fov',
		'seen',
		'_force_update'
	)

	def __init__(self, player, terrain):
		self._player = player
		self._dim = terrain.dim
		self._map = tcod.map.Map(*terrain.dim)
		self._map.transparent[:] = True
		self._force_update = False
		self.fov = NumpyMapSet(self._map.fov)
		self.seen = set()
		self.setup_terrain(terrain)
		events.move.on.add(self.watch_player_move, priority=1)
		events.acted.on.add(self.watch_acted)
		events.terrain_change.on.add(self.watch_terrain_change)
		if player in props.position:
			self.update_fov(props.position[player])

	def setup_terrain(self, terrain):
		for x in range(0, terrain.dim[0]):
			for y in range(0, terrain.dim[1]):
				if terrain[x, y] in props.blocks_vision:
					self._map.transparent[y, x] = False

	def watch_terrain_change(self, pos):
		x, y = pos
		self._map.transparent[y, x] = props.terrain_at[pos] not in props.blocks_vision
		self._force_update = True

	def watch_player_move(self, actor, move_from, move_to):
		if actor == self._player:
			self.update_fov(move_to)

	def watch_acted(self, actor):
		if self._force_update:
			if self._player in props.position:
				self.update_fov(props.position[self._player])
			self._force_update = False

	def update_fov(self, pos):
			self._map.compute_fov(*pos, radius=fov_range, algorithm=tcod.FOV_BASIC)
			self.update_seen(pos)

	def update_seen(self, centre):
		for x in range(max(0, centre[0] - fov_range), min(self._dim[0], centre[0] + fov_range + 1)):
			for y in range(max(0, centre[1] - fov_range), min(self._dim[1], centre[1] + fov_range + 1)):
				if self._map.fov[y, x]:
					self.seen.add((x, y))

class NumpyMapSet(data.BaseProperty):
	__slots__ = (
		'map',
		'default'
	)

	def __init__(self, map, default=None):
		self.map = map
		self.default = default

	def __contains__(self, pos):
		try:
			x, y = pos
		except TypeError:
			return False
		return self.map[y, x]

	def __getitem__(self, pos):
		try:
			x, y = pos
		except TypeError:
			return self.default
		try:
			return self.map[y, x]
		except:
			return self.default

	def __setitem__(self, pos, value):
		try:
			x, y = pos
		except TypeError:
			return self.default
		try:
			self.map[y, x] = value
		except:
			return self.default
