import numpy
from .. import ui
from .. import game
from ..game import properties as props
from ..game import events
from ..game import actions
from . import commands

class TopBarWin(ui.Window):
	__slots__ = (
		'_game',
	)

	def __init__(self, game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self.on_redraw.add(self.redraw)

	def redraw(self, console):
		ap = props.action_points_this_turn[self._game.player]
		ap_str = int(ap) if int(ap) == ap else "%0.2f" % (ap)
		console.clear()
		console.draw_str(0, 0, f'AP: {ap_str} Pop: {props.population[self._game.player]}')

class MapWin(ui.Window):
	__slots__ = (
		'_game',
		'_player_actions',
		'_view_centre',
		'_free_view'
	)

	def __init__(self, game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self.on_redraw.add(self.redraw)
		self._player_actions = []
		self._free_view = False
		self.setup_keys()
		self.view_centre()

	def redraw(self, console):
		view_centre = self.view_centre()
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

	def view_centre(self):
		if self._free_view:
			return self._view_centre
		else:
			pos = props.position[self._game.player]
			self._view_centre = pos
			return pos

	def setup_keys(self):
		self.on_key[commands.move_n].add(self.player_mover((0, -1)))
		self.on_key[commands.move_s].add(self.player_mover((0, 1)))
		self.on_key[commands.move_e].add(self.player_mover((1, 0)))
		self.on_key[commands.move_w].add(self.player_mover((-1, 0)))
		self.on_key[commands.move_ne].add(self.player_mover((1, -1)))
		self.on_key[commands.move_nw].add(self.player_mover((-1, -1)))
		self.on_key[commands.move_se].add(self.player_mover((1, 1)))
		self.on_key[commands.move_sw].add(self.player_mover((-1, 1)))
		self.on_key[commands.pass_turn].add(self.player_skip)
		self.on_key[commands.centre_view].add(self.stop_free_view)
		self.on_key[commands.move_view_n].add(self.view_mover((0, -1)))
		self.on_key[commands.move_view_s].add(self.view_mover((0, 1)))
		self.on_key[commands.move_view_e].add(self.view_mover((1, 0)))
		self.on_key[commands.move_view_w].add(self.view_mover((-1, 0)))
		self.on_key[commands.move_view_ne].add(self.view_mover((1, -1)))
		self.on_key[commands.move_view_nw].add(self.view_mover((-1, -1)))
		self.on_key[commands.move_view_se].add(self.view_mover((1, 1)))
		self.on_key[commands.move_view_sw].add(self.view_mover((-1, 1)))

	def stop_free_view(self):
		self._free_view = False

	def player_skip(self):
		self._player_actions.append(actions.SkipTurn(self._game.player))

	def player_mover(self, delta):
		def handler():
			self._free_view = False
			self._player_actions.append(actions.Move(self._game.player, delta))
		return handler

	def view_mover(self, delta, multiplier=10):
		def handler():
			self._free_view = True
			self._view_centre = tuple(self._view_centre[i] + delta[i] * multiplier for i in range(2))
		return handler

class MainView(ui.View):
	__slots__ = (
		'_display',
		'_full_keybindings',
		'_game',
		'_top_bar_win',
		'_map_win'
	)

	def __init__(self, display, full_keybindings, the_game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._full_keybindings = full_keybindings
		self._game = the_game
		self._top_bar_win = TopBarWin(self._game)
		self._map_win = MapWin(self._game, keybindings=self.keybindings)
		self.windows.add(self._top_bar_win)
		self.windows.add(self._map_win)
		self.on_resize.add(self.resize)
		self.on_before_redraw.add(self.update_game)
		events.act.on.add(self.take_player_action)
		events.win.on.add(self.win_or_lose, priority=99)
		events.lose.on.add(self.win_or_lose, priority=99)
		self.on_key[commands.quit].add(self._display.quit)

	def take_player_action(self, thing, available_ap):
		if thing == self._game.player:
			actions = tuple(self._map_win._player_actions)
			self._map_win._player_actions.clear()
			return actions
		else:
			return None

	def win_or_lose(self, player):
		self.close()

	def update_game(self):
		self._game.update()

	def resize(self, dim):
		self._top_bar_win.place((0, 0), (dim[0], 1))
		self._map_win.place((0, 1), (dim[0], dim[1] - 1))
