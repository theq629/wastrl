import collections
from .. import data

class MapProperty:
	__slots__ = (
		'map',
	)

	def __getitem__(self, pos):
		return self.map[pos]

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
graphics = data.ValuedProperty()
position = data.ValuedProperty()
population = data.ValuedProperty()
inventory = data.ValuedProperty()
action_points = data.ValuedProperty()
action_points_this_turn = data.ValuedProperty()
walk_over_ap = data.ValuedProperty()
attack = data.ValuedProperty()
activation_target_range = data.ValuedProperty()

is_goal = data.SetProperty()
is_player = data.SetProperty()

terrain_at = MapProperty()
things_at = MapProperty()
