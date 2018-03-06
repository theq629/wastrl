import collections
import math
import tcod.random
from .. import data
from . import mapgen
import sys # TODO

Graphics = collections.namedtuple('Graphics', ('char', 'colour'))

has_actions = data.Property()
has_actions_this_turn = data.Property()
act = data.Event(None, lambda a, b: a if a is not None else b)
turn = data.Event()
_to_act_this_turn = data.Property()

graphics = data.Property()

position = data.Property()

class Move:
	__slots__ = (
		'_actor',
		'_delta',
		'_ap'
	)

	def __init__(self, actor, delta):
		self._actor = actor
		self._delta = delta
		self._ap = self._calc_ap(delta)

	def _calc_ap(self, delta):
		x, y = delta
		return math.sqrt(x**2 + y**2)
	
	@property
	def ap(self):
		return self._ap

	def trigger(self):
		position[self._actor] = tuple(position[self._actor][i] + self._delta[i] for i in range(2))

class SkipTurn:
	__slots__ = (
		'_ap',
	)

	def __init__(self, actor):
		self._ap = has_actions_this_turn[actor]
	
	@property
	def ap(self):
		return self._ap

	def trigger(self):
		pass

@turn.on.handle(0)
def handle_thing_turns(min_ap=1):
	def try_start_new_turn():
		if len(_to_act_this_turn) == 0:
			print("start turn", file=sys.stderr)
			for thing, ap in has_actions.items():
				if ap > 0:
					has_actions_this_turn[thing] = ap
					_to_act_this_turn[thing] = None
	
	try_start_new_turn()

	# TODO: add easy function for zipping
	for thing in _to_act_this_turn.keys():
		cur_ap = has_actions_this_turn[thing]
		actions = act.trigger(thing, cur_ap)
		for action in actions:
			if cur_ap < action.ap:
				break
			cur_ap -= action.ap
			action.trigger()
		print("thing %i acting: %s actions, %i ap remaining" % (thing.index, str(len(actions)) if actions is not None else 'no', cur_ap), file=sys.stderr)
		has_actions_this_turn[thing] = cur_ap
		if cur_ap <= min_ap:
			_to_act_this_turn.remove(thing)
		break
	
	try_start_new_turn()

class Game:
	def __init__(self, seed):
		self.rng = tcod.random.Random(tcod.random.MERSENNE_TWISTER, seed=seed)
		self.terrain, starting_point, ending_point = mapgen.gen(self.rng)
		self.player = data.Thing()
		has_actions[self.player] = 5
		position[self.player] = starting_point
		graphics[self.player] = Graphics(char='@', colour=0xffffff)

	def update(self):
		turn.trigger()
