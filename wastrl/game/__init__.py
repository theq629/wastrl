import collections
import tcod.random
from .. import data
from . import mapgen
from . import thingsgen
from . import properties as props
from . import events
import sys # TODO: improve logging

_to_act_this_turn = data.SetProperty()

@events.turn.on.handle(0)
def handle_thing_turns(min_ap=1):
	def try_start_new_turn():
		if len(_to_act_this_turn) == 0:
			print("start turn", file=sys.stderr)
			for thing, ap in props.action_points.items():
				if ap > 0:
					props.action_points_this_turn[thing] = ap
					_to_act_this_turn.add(thing)
	
	try_start_new_turn()

	done = set()
	for thing in _to_act_this_turn:
		cur_ap = props.action_points_this_turn[thing]
		actions = events.act.trigger(thing, cur_ap)
		if actions is None:
			done.add(thing)
		else:
			for action in actions:
				if action.ap is not None:
					if cur_ap < action.ap:
						break
					cur_ap -= action.ap
					action.trigger()
			print("thing %i acting: %s actions, %i ap remaining" % (thing.index, str(len(actions)) if actions is not None else 'no', cur_ap), file=sys.stderr)
			props.action_points_this_turn[thing] = cur_ap
			if cur_ap <= min_ap:
				done.add(thing)
				break
	for thing in done:
		_to_act_this_turn.remove(thing)
	
	try_start_new_turn()

@events.turn.on.handle(1000)
def check_win():
	for player, player_pos in props.is_player.join(props.position):
		for goal, goal_pos in props.is_goal.join(props.position):
			if goal_pos == player_pos:
				events.win.trigger(player)

class Game:
	def __init__(self, seed):
		self.rng = tcod.random.Random(tcod.random.MERSENNE_TWISTER, seed=seed)
		self.terrain, starting_point, ending_point, city_points = mapgen.gen(self.rng)

		props.terrain_at.map = self.terrain

		thingsgen.gen(self.terrain, self.rng)

		for point in city_points:
			city = things.city()
			props.position[city] = point

		goal = things.goal()
		props.position[goal] = ending_point

		self.player = things.player()
		props.position[self.player] = starting_point

	def update(self):
		events.turn.trigger()
