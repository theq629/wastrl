import collections
import tcod.random
from .. import data
from . import mapgen
from . import thingsgen
from . import properties as props
from . import events
from . import utils
from . import ai
from . import tilemap
import sys # TODO: improve logging

class TurnManager:
	__slots__ = (
		'_min_ap',
		'_to_act_this_turn',
		'_taking_turn',
		'_action_this_update'
	)

	def __init__(self, min_ap=1):
		self._min_ap = min_ap
		self._to_act_this_turn = data.OrderedSetProperty()
		self._taking_turn = None
		self._action_this_update = False
		self._start_turn()
		events.act.on.add(self._handle_action)

	def update(self):
		self._action_this_update = False
		if self._taking_turn is None or props.action_points_this_turn[self._taking_turn] < self._min_ap:
			if self._taking_turn is not None:
				self._to_act_this_turn.remove(self._taking_turn)
		if len(self._to_act_this_turn) == 0:
			self._start_turn()
		self._taking_turn = next(iter(self._to_act_this_turn))
		events.take_turn.trigger(self._taking_turn)
		if self._action_this_update:
			return self._taking_turn
		else:
			return None

	def _start_turn(self):
		for thing, ap in props.action_points.items():
			if thing in props.is_player:
				props.action_points_this_turn[thing] = ap
				self._to_act_this_turn.add(thing)
		for thing, ap in props.action_points.items():
			if thing not in props.is_player:
				props.action_points_this_turn[thing] = ap
				self._to_act_this_turn.add(thing)

	def _handle_action(self, actor, action):
		if actor != self._taking_turn:
			print(f"warning: actor {actor.index} acting out of turn")
		else:
			if action.ap is None or action.ap > props.action_points_this_turn[actor]:
				print(f"warning: actor {actor.index} requested impossible action")
				if actor not in props.is_player:
					_to_act_this_turn.remove(self._taking_turn)
			else:
				action.trigger()
				props.action_points_this_turn[actor] -= action.ap
				events.acted.trigger(actor)
				self._action_this_update = True

@events.turn.on.handle(1000)
def check_win():
	for player, player_pos in props.is_player.join(props.position):
		for goal, goal_pos in props.is_goal.join(props.position):
			if goal_pos == player_pos:
				events.win.trigger(player)

@events.move.on.handle(-1)
def update_things_at(thing, move_from, move_to):
	if move_from is not None:
		props.things_at[move_from].remove(thing)
	if move_to is not None:
		props.things_at[move_to].add(thing)

class Game:
	def __init__(self, seed):
		self.rng = tcod.random.Random(tcod.random.MERSENNE_TWISTER, seed=seed)
		self.terrain, starting_point, ending_point, city_points = mapgen.gen(self.rng)

		props.terrain_at.map = self.terrain
		props.things_at.map = tilemap.Tilemap(self.terrain.dim, init=lambda _: set())
		ai.Ai(self.terrain)

		thingsgen.gen(self.terrain, self.rng)

		for point in city_points:
			utils.spawn(things.city(), point)
		utils.spawn(things.goal(), ending_point)
		player = things.player()
		utils.spawn(player, starting_point)

		print("player:", player.index, file=sys.stderr)

		self.turn_manager = TurnManager()
		self.turn_manager.update()

	def update(self):
		changed = False
		while True:
			acted = self.turn_manager.update()
			if acted is None:
				break
			changed = True
		return changed
