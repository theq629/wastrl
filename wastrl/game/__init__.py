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
from .logic import turns as logic_turns
from .logic import fov as logic_fov
from .logic import examine as logic_examine
from .logic import mortality as logic_mortality
from .logic import win_lose as logic_win_lose
from .logic import single_use as logic_single_use
from .logic import starter_kit as logic_starter_kit
import sys # TODO: improve logging

@events.move.on.handle(-1)
def update_things_at(thing, move_from, move_to):
	if move_from is not None:
		props.things_at[move_from].remove(thing)
		props.blocked_at[move_from] = any(t in props.is_blocking for t in props.things_at[move_from])
	if move_to is not None:
		props.things_at[move_to].add(thing)
		props.blocked_at[move_to] |= thing in props.is_blocking

def reset_data():
	all_things = set(props.position) | set(t for i in props.inventory.values() for t in i)
	for thing in all_things:
		data.BaseProperty.all.remove(thing)

class Game:
	def __init__(self, seed, starter_kit=False, log_things_gen=False):
		self.rng = tcod.random.Random(tcod.random.MERSENNE_TWISTER, seed=seed)
		self.terrain, starting_point, ending_point, city_points, mountain_spines = mapgen.gen(self.rng)

		reset_data()

		props.terrain_at.map = self.terrain
		props.terrain_at.default = things.desert
		props.things_at.map = tilemap.Tilemap(self.terrain.dim, init=lambda _: set())
		props.blocked_at.map = tilemap.Tilemap(self.terrain.dim, init=lambda _: False)
		ai.Ai(self.rng, self.terrain)

		thingsgen.gen(self.terrain, mountain_spines, city_points, self.rng, debug_log=log_things_gen)

		for point in city_points:
			utils.spawn(things.city(), point)
		utils.spawn(things.goal(), ending_point)
		player = things.player()
		utils.spawn(player, starting_point)
		self._player = player

		print("player:", player, file=sys.stderr)

		if starter_kit:
			thingsgen.set_starting_kit(player)

		self.turn_manager = logic_turns.TurnManager(self.rng)

		fover = logic_fov.Fover(self._player, self.terrain)
		props.fov[self._player] = fover.fov
		props.seen_fov[self._player] = fover.seen

	def update(self):
		changed = False
		while self._player in props.is_alive:
			acted, changed_now = self.turn_manager.update(self.rng)
			changed |= changed_now
			if acted is None or changed_now:
				break
			changed = True
		return changed
