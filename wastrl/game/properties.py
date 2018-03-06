import collections
from .. import data

Graphics = collections.namedtuple('Graphics', ('char', 'colour'))

named = data.ValuedProperty()
graphics = data.ValuedProperty()
position = data.ValuedProperty()
is_goal = data.SetProperty()
action_points = data.ValuedProperty()
action_points_this_turn = data.ValuedProperty()
