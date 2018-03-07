import numpy
from .. import ui
from .. import game
from ..game import properties as props
from ..game import events
from ..game import actions
from . import commands

class PlayerController:
	__slots__ = (
		'_player',
		'_on_key',
		'_is_our_turn'
	)

	def __init__(self, player, on_key):
		self._player = player
		self._on_key = on_key
		self._is_our_turn = False
		events.take_turn.on.add(self.watch_turn)
		self.setup_keys()

	def setup_keys(self):
		self._on_key[commands.pass_turn].add(self.command_skip)
		self._on_key[commands.move_n].add(self.command_mover((0, -1)))
		self._on_key[commands.move_s].add(self.command_mover((0, 1)))
		self._on_key[commands.move_e].add(self.command_mover((1, 0)))
		self._on_key[commands.move_w].add(self.command_mover((-1, 0)))
		self._on_key[commands.move_ne].add(self.command_mover((1, -1)))
		self._on_key[commands.move_nw].add(self.command_mover((-1, -1)))
		self._on_key[commands.move_se].add(self.command_mover((1, 1)))
		self._on_key[commands.move_sw].add(self.command_mover((-1, 1)))
		self._on_key[commands.get].add(self.command_get)
		self._on_key[commands.drop].add(self.command_drop)

	def command_skip(self):
		if self._is_our_turn:
			events.act.trigger(self._player, actions.SkipTurn(self._player))

	def command_get(self):
		if self._is_our_turn:
			things = set(t for t in props.things_at[props.position[self._player]] if t != self._player)
			events.act.trigger(self._player, actions.Get(self._player, things))

	def command_drop(self):
		if self._is_our_turn:
			events.act.trigger(self._player, actions.Drop(self._player, set(props.inventory[self._player])))

	def command_mover(self, delta):
		def handle():
			if self._is_our_turn:
				events.act.trigger(self._player, actions.Move(self._player, delta))
		return handle

	def watch_turn(self, actor):
		self._is_our_turn = actor == self._player

class ViewController:
	__slots__ = (
		'_player',
		'_on_key',
		'_view_centre',
		'_free_view'
	)

	def __init__(self, player, on_key):
		self._player = player
		self._on_key = on_key
		self._free_view = False
		self.view_centre
		self.setup_keys()

	def setup_keys(self):
		self._on_key[commands.centre_view].add(self.stop_free_view)
		self._on_key[commands.move_view_n].add(self.view_mover((0, -1)))
		self._on_key[commands.move_view_s].add(self.view_mover((0, 1)))
		self._on_key[commands.move_view_e].add(self.view_mover((1, 0)))
		self._on_key[commands.move_view_w].add(self.view_mover((-1, 0)))
		self._on_key[commands.move_view_ne].add(self.view_mover((1, -1)))
		self._on_key[commands.move_view_nw].add(self.view_mover((-1, -1)))
		self._on_key[commands.move_view_se].add(self.view_mover((1, 1)))
		self._on_key[commands.move_view_sw].add(self.view_mover((-1, 1)))

	@property
	def view_centre(self):
		if self._free_view:
			return self._view_centre
		else:
			pos = props.position[self._player]
			self._view_centre = pos
			return pos

	def stop_free_view(self):
		self._free_view = False

	def view_mover(self, delta, multiplier=10):
		def handler():
			self._free_view = True
			self._view_centre = tuple(self._view_centre[i] + delta[i] * multiplier for i in range(2))
		return handler

class TopBarWin(ui.Window):
	__slots__ = (
		'_player',
	)

	def __init__(self, player, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._player = player
		self.on_redraw.add(self.redraw)

	def redraw(self, console):
		ap = props.action_points_this_turn[self._player]
		ap_str = int(ap) if int(ap) == ap else "%0.2f" % (ap)
		console.clear()
		console.draw_str(0, 0, f'AP: {ap_str} Pop: {props.population[self._player]}')

class MapWin(ui.Window):
	__slots__ = (
		'_game',
		'_player',
		'_player_actions',
		'_view_controller',
		'_free_view'
	)

	def __init__(self, game, player, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self._player = player
		self.on_redraw.add(self.redraw)
		self._player_actions = []
		self._view_controller = ViewController(self._player, self.on_key)
		PlayerController(self._player, self.on_key)
		events.move.on.add(self.watch_move)

	def watch_move(self, actor, move_from, move_to):
		if actor == self._player:
			self._view_controller.stop_free_view()

	def redraw(self, console):
		view_centre = self._view_controller.view_centre
		world_dim = self._game.terrain.dim
		world_offset = tuple(view_centre[i] - int(self.dim[i] / 2) for i in range(2))
		screen_bounds = tuple((max(0, -world_offset[i]), min(self.dim[i], world_dim[i] - world_offset[i])) for i in range(2))

		console.clear()

		for screen_x in range(*screen_bounds[0]):
			for screen_y in range(*screen_bounds[1]):
				world_x, world_y = world_offset[0] + screen_x, world_offset[1] + screen_y
				terrain = self._game.terrain[world_x, world_y]
				graphic = props.graphics[terrain]
				console.draw_char(screen_x, screen_y, char=graphic.char, fg=graphic.colour)

		# TODO: cache
		for thing, graphic, (world_x, world_y) in props.graphics.join_keys(props.position):
			screen_x, screen_y = world_x - world_offset[0], world_y - world_offset[1]
			if screen_x >= 0 and screen_x < self.dim[0] and screen_y >= 0 and screen_y < self.dim[1]:
				console.draw_char(screen_x, screen_y, char=graphic.char, fg=graphic.colour)

class MainView(ui.View):
	__slots__ = (
		'_display',
		'_full_keybindings',
		'_game',
		'_player',
		'_top_bar_win',
		'_map_win'
	)

	def __init__(self, display, full_keybindings, the_game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._full_keybindings = full_keybindings
		self._game = the_game
		self._player = next(iter(props.is_player))
		self._top_bar_win = TopBarWin(self._player)
		self._map_win = MapWin(self._game, self._player, keybindings=self.keybindings)
		self.windows.add(self._top_bar_win)
		self.windows.add(self._map_win)
		self.on_resize.add(self.resize)
		self.on_frame.add(self.update_game)
		events.act.on.add(self.take_player_action)
		events.win.on.add(self.win_or_lose, priority=99)
		events.lose.on.add(self.win_or_lose, priority=99)
		self.on_key[commands.quit].add(self._display.quit)

	def take_player_action(self, thing, available_ap):
		if thing == self._player:
			actions = tuple(self._map_win._player_actions)
			self._map_win._player_actions.clear()
			return actions
		else:
			return None

	def win_or_lose(self, player):
		self.close()

	def update_game(self):
		return self._game.update()

	def resize(self, dim):
		self._top_bar_win.place((0, 0), (dim[0], 1))
		self._map_win.place((0, 1), (dim[0], dim[1] - 1))
