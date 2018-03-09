import collections
from .. import data

class MapProperty(data.BaseProperty):
	__slots__ = (
		'map',
	)

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
			raise KeyError()
		return self.map[pos]

	def __setitem__(self, pos, value):
		try:
			x, y = pos
		except TypeError:
			raise KeyError()
		self.map[pos] = value

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

is_goal = data.SetProperty()
is_player = data.SetProperty()

terrain_at = MapProperty()
things_at = MapProperty()
blocked_at = MapProperty()
