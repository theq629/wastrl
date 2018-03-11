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
		'seen'
	)

	def __init__(self, player, terrain):
		self._player = player
		self._dim = terrain.dim
		self._map = tcod.map.Map(*terrain.dim)
		self._map.transparent[:] = True
		self.fov = NumpyMapSet(self._map.fov)
		self.seen = set()
		self.setup_terrain(terrain)
		events.move.on.add(self.update_fov, priority=1)
		if player in props.position:
			self.update_fov(player, None, props.position[player])

	def setup_terrain(self, terrain):
		for x in range(0, terrain.dim[0]):
			for y in range(0, terrain.dim[1]):
				if terrain[x, y] in props.blocks_vision:
					self._map.transparent[y, x] = False

	def update_fov(self, actor, move_from, move_to):
		if actor == self._player:
			self._map.compute_fov(*move_to, radius=fov_range, algorithm=tcod.FOV_BASIC)
			self.update_seen(move_to)

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
