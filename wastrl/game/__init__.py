import sys
import traceback
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
		'_rng',
		'_min_ap',
		'_to_act_this_turn',
		'_taking_turn',
		'_action_this_update'
	)

	def __init__(self, rng, min_ap=1):
		self._rng = rng
		self._min_ap = min_ap
		self._to_act_this_turn = data.OrderedSetProperty()
		self._taking_turn = None
		self._action_this_update = False
		self._start_turn()
		events.act.on.add(self._handle_action)
		events.die.on.add(self._handle_death)

	def update(self, rng):
		event_change = False

		self._action_this_update = False
		if self._taking_turn is None or self._taking_turn not in props.action_points_this_turn or props.action_points_this_turn[self._taking_turn] < self._min_ap:
			if self._taking_turn is not None:
				if self._taking_turn in self._to_act_this_turn:
					self._to_act_this_turn.remove(self._taking_turn)
				self._taking_turn = None
		if len(self._to_act_this_turn) == 0:
			self._start_turn()

		event_change |= events.update.trigger(rng)

		if len(self._to_act_this_turn) > 0:
			next_to_go = next(iter(self._to_act_this_turn))
			if next_to_go != self._taking_turn:
				self._taking_turn = next_to_go
				events.take_turn.trigger(self._taking_turn)

		event_change = event_change
		if self._action_this_update:
			return self._taking_turn, event_change
		else:
			return None, event_change

	def _start_turn(self):
		for thing, ap in props.action_points.items():
			if thing in props.is_player:
				props.action_points_this_turn[thing] = ap
				self._to_act_this_turn.add(thing)
		for thing, ap in props.action_points.items():
			if thing not in props.is_player:
				props.action_points_this_turn[thing] = ap
				self._to_act_this_turn.add(thing)
		events.start_turn.trigger(self._rng)

	def _handle_action(self, actor, action):
		if actor != self._taking_turn:
			print(f"warning: actor {actor.index} acting out of turn")
		else:
			if action.ap is None or action.ap > props.action_points_this_turn[actor]:
				print(f"warning: actor {actor.index} requested impossible action")
				if actor not in props.is_player:
					_to_act_this_turn.remove(self._taking_turn)
			else:
				try:
					action.trigger(self._rng)
					if actor in props.action_points_this_turn:
						props.action_points_this_turn[actor] -= action.ap
				except Exception as e:
					print("error in action:", file=sys.stderr)
					traceback.print_exc(file=sys.stderr)
					if actor in _to_act_this_turn:
						_to_act_this_turn.remove(actor)
				events.acted.trigger(actor)
				self._action_this_update = True

	def _handle_death(self, actor):
		if actor in self._to_act_this_turn:
			self._to_act_this_turn.remove(actor)

@events.attack.on.handle(1000)
def handle_damage(attackee, target, damage):
	if target in props.is_alive:
		props.population[target] -= damage
		events.take_damage.trigger(target, damage)

@events.take_damage.on.handle(1000)
def handle_death(thing, damage):
	if props.population[thing] <= 0:
		pos = props.position[thing]
		props.population[thing] = 0
		props.is_alive.remove(thing)
		props.is_dead.add(thing)
		props.action_points.remove(thing)
		props.action_points_this_turn.remove(thing)
		props.position.remove(thing)
		events.move.trigger(thing, pos, None)
		events.die.trigger(thing)

@events.move.on.handle(1000)
def check_win(actor, move_from, move_to):
	if actor in props.is_player:
		for goal, goal_pos in props.is_goal.join(props.position):
			if goal_pos == move_to:
				events.win.trigger(actor)

@events.die.on.handle(1000)
def check_lose(actor):
	if actor in props.is_player:
		events.lose.trigger(actor)

@events.move.on.handle(-1)
def update_things_at(thing, move_from, move_to):
	if move_from is not None:
		props.things_at[move_from].remove(thing)
		props.blocked_at[move_from] = any(t in props.is_blocking for t in props.things_at[move_from])
	if move_to is not None:
		props.things_at[move_to].add(thing)
		props.blocked_at[move_to] |= thing in props.is_blocking

@events.examine.on.handle(0)
def base_examine(thing):
	if thing not in props.name:
		return ""
	else:
		name = props.name[thing]
		article = None
		if thing in props.name_article:
			article = props.name_article[thing]
		else:
			if len(name) > 0:
				article = "an" if name[0].lower() in "aeiou" else "a"
		if article is not None:
			name = " ".join((article, name))
		return name

def reset_data():
	all_things = set(props.position) | set(t for i in props.inventory.values() for t in i)
	for thing in all_things:
		data.BaseProperty.all.remove(thing)

class Game:
	def __init__(self, seed):
		self.rng = tcod.random.Random(tcod.random.MERSENNE_TWISTER, seed=seed)
		self.terrain, starting_point, ending_point, city_points = mapgen.gen(self.rng)

		reset_data()

		props.terrain_at.map = self.terrain
		props.things_at.map = tilemap.Tilemap(self.terrain.dim, init=lambda _: set())
		props.blocked_at.map = tilemap.Tilemap(self.terrain.dim, init=lambda _: False)
		ai.Ai(self.rng, self.terrain)

		thingsgen.gen(self.terrain, self.rng)

		for point in city_points:
			utils.spawn(things.city(), point)
		utils.spawn(things.goal(), ending_point)
		player = things.player()
		utils.spawn(player, starting_point)
		self._player = player

		print("player:", player.index, file=sys.stderr)

		thingsgen.set_starting_kit(player) # TODO: debugging

		self.turn_manager = TurnManager(self.rng)

	def update(self):
		changed = False
		while self._player in props.is_alive:
			acted, changed_now = self.turn_manager.update(self.rng)
			changed |= changed_now
			if acted is None or changed_now:
				break
			changed = True
		return changed
