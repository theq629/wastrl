import collections
from .. import data

class MapProperty:
	__slots__ = (
		'map',
	)

	def __getitem__(self, pos):
		return self.map[pos]

Graphics = collections.namedtuple('Graphics', ('char', 'colour'))

named = data.ValuedProperty()
graphics = data.ValuedProperty()
position = data.ValuedProperty()
is_goal = data.SetProperty()
is_player = data.SetProperty()
population = data.ValuedProperty()
action_points = data.ValuedProperty()
action_points_this_turn = data.ValuedProperty()
walk_over_ap = data.ValuedProperty()
terrain_at = MapProperty()
