import collections
from .. import data

class MapProperty(data.BaseProperty):
	__slots__ = (
		'map',
		'default'
	)

	def __init__(self, default=None):
		self.map = None
		self.default = default

	def __contains__(self, pos):
		try:
			x, y = pos
		except TypeError:
			return False
		return x >= 0 and x < self.map.dim[0] and y >= 0 and y < self.map.dim[1]

	def __getitem__(self, pos):
		try:
			x, y = pos
		except TypeError:
			return self.default
		try:
			return self.map[pos]
		except:
			return self.default

	def __setitem__(self, pos, value):
		try:
			x, y = pos
		except TypeError:
			return self.default
		try:
			self.map[pos] = value
		except:
			return self.default

	def clear(self):
		pass

Graphics = collections.namedtuple('Graphics', (
	'char',
	'colour'
))

Attack = collections.namedtuple('Attack', (
	'damage'
))

ActivationTargetRange = collections.namedtuple('ActivationTargetRange', (
	'move_range',
	'fire_range'
))

name = data.ValuedProperty()
name_article = data.ValuedProperty()
graphics = data.ValuedProperty()
position = data.ValuedProperty()
population = data.ValuedProperty()
intrinsics = data.ValuedProperty()
inventory = data.ValuedProperty()
action_points = data.ValuedProperty()
action_points_this_turn = data.ValuedProperty()
walk_over_ap = data.ValuedProperty()
attack = data.ValuedProperty()
activation_target_range = data.ValuedProperty()
is_alive = data.SetProperty()
is_dead = data.SetProperty()
is_visual = data.SetProperty()
is_blocking = data.SetProperty()
blocks_vision = data.SetProperty()
blocks_local_vision = data.SetProperty()
is_flamable = data.SetProperty()
is_guarding_city = data.SetProperty()
fov = data.ValuedProperty()
seen_fov = data.ValuedProperty()
single_use = data.SetProperty()
is_from_starter_kit = data.SetProperty()
suppresses_fire = data.SetProperty()

is_goal = data.SetProperty()
is_player = data.SetProperty()

terrain_at = MapProperty()
things_at = MapProperty(set())
blocked_at = MapProperty(False)
