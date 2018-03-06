import numpy
from .. import ui
from .. import game
from ..game import things

class TopBarWin(ui.Window):
	__slots__ = (
		'_game',
	)

	def __init__(self, game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self.on_redraw.add(self.redraw)

	def redraw(self, console):
		ap = game.has_actions_this_turn[self._game.player]
		ap_str = str(int(ap)) if int(ap) == ap else str(ap)
		console.draw_str(0, 0, f'AP: {ap_str}')

class MapWin(ui.Window):
	__slots__ = (
		'_game',
		'_max_height',
		'_draw_cell',
		'_player_actions'
	)

	def __init__(self, game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self._max_height = max(numpy.nditer(self._game.height))
		self.on_redraw.add(self.redraw)
		self.on_key.add(self.key)
		self._draw_cell = self.draw_terrain_cell
		self._player_actions = []

	def view_centre(self):
		return game.position[self._game.player]

	def redraw(self, console):
		view_centre = self.view_centre()
		world_dim = tuple(reversed(self._game.height.shape))
		world_offset = tuple(view_centre[i] - int(self.dim[i] / 2) for i in range(2))
		screen_bounds = tuple((max(0, -world_offset[i]), min(self.dim[i], world_dim[i] - world_offset[i])) for i in range(2))
		console.clear()
		for screen_x in range(*screen_bounds[0]):
			for screen_y in range(*screen_bounds[1]):
				world_x, world_y = world_offset[0] + screen_x, world_offset[1] + screen_y
				self._draw_cell(console, screen_x, screen_y, world_x, world_y)

		# TODO: cache
		# TODO: add easy joins on properties
		for thing, graphic in game.graphics.items():
			try:
				world_x, world_y = game.position[thing]
				screen_x, screen_y = world_x - world_offset[0], world_y - world_offset[1]
				if screen_x >= 0 and screen_x < self.dim[0] and screen_y >= 0 and screen_y < self.dim[1]:
					console.draw_char(screen_x, screen_y, char=graphic.char, fg=graphic.colour)
			except KeyError:
				pass

	def draw_terrain_cell(self, console, screen_x, screen_y, world_x, world_y):
		terrain = self._game.terrain[world_x, world_y]
		console.draw_char(screen_x, screen_y, char=things.characters[terrain], fg=things.colours[terrain])

	def draw_height_cell(self,console,  screen_x, screen_y, world_x, world_y):
		c = int(255 * (self._game.height[world_y, world_x] / self._max_height))
		console.draw_char(screen_x, screen_y, char='.', fg=(c, c, c))

	def key(self, key):
		if key == 'UP' or key == 'k':
			self._player_actions.append(game.Move(self._game.player, (0, -1)))
			return True
		elif key == 'DOWN' or key == 'j':
			self._player_actions.append(game.Move(self._game.player, (0, 1)))
			return True
		elif key == 'LEFT' or key == 'h':
			self._player_actions.append(game.Move(self._game.player, (-1, 0)))
			return True
		elif key == 'RIGHT' or key == 'l':
			self._player_actions.append(game.Move(self._game.player, (1, 0)))
			return True
		elif key == 'shift+UP' or key == 'shift+k':
			self._view_centre[1] -= 10
			return True
		elif key == 'shift+DOWN' or key == 'shift+j':
			self._view_centre[1] += 10
			return True
		elif key == 'shift+LEFT' or key == 'shift+h':
			self._view_centre[0] -= 10
			return True
		elif key == 'shift+RIGHT' or key == 'shift+l':
			self._view_centre[0] += 10
			return True
		elif key == '1':
			self._draw_cell = self.draw_terrain_cell
			return True
		elif key == '2':
			self._draw_cell = self.draw_height_cell
			return True

class MainView(ui.View):
	__slots__ = (
		'_display',
		'_game',
		'_top_bar_win',
		'_map_win'
	)

	def __init__(self, display, the_game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._game = the_game
		self._top_bar_win = TopBarWin(self._game)
		self._map_win = MapWin(self._game)
		self.windows.add(self._top_bar_win)
		self.windows.add(self._map_win)
		self.on_resize.add(self.resize)
		self.on_key.add(self.key)
		self.on_before_redraw.add(self.update_game)
		game.act.on.add(self.take_player_action)

	def take_player_action(self, thing, available_ap):
		if thing == self._game.player:
			actions = tuple(self._map_win._player_actions)
			self._map_win._player_actions.clear()
			return actions
		else:
			return None

	def update_game(self):
		self._game.update()

	def resize(self, dim):
		self._top_bar_win.place((0, 0), (dim[0], 1))
		self._map_win.place((0, 1), (dim[0], dim[1] - 1))

	def key(self, key):
		if key == 'q':
			self._display.quit()
			return True
