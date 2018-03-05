import numpy
from .. import ui

class TopBarWin(ui.Window):
	__slots__ = ()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.on_redraw.add(self.redraw)

	def redraw(self, console):
		console.draw_str(0, 0, 'Wastrl')

class MapWin(ui.Window):
	__slots__ = (
		'_game',
		'_view_centre',
		'_max_height'
	)

	def __init__(self, game, view_centre, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self._view_centre = list(view_centre)
		self._max_height = max(numpy.nditer(self._game.height))
		self.on_redraw.add(self.redraw)
		self.on_key.add(self.key)

	def redraw(self, console):
		world_dim = tuple(reversed(self._game.height.shape))
		world_offset = tuple(self._view_centre[i] - int(self.dim[i] / 2) for i in range(2))
		screen_bounds = tuple((max(0, -world_offset[i]), min(self.dim[i], world_dim[i] - world_offset[i])) for i in range(2))
		console.clear()
		for screen_x in range(*screen_bounds[0]):
			for screen_y in range(*screen_bounds[1]):
				world_x, world_y = world_offset[0] + screen_x, world_offset[1] + screen_y
				c = int(255 * (self._game.height[world_y, world_x] / self._max_height))
				console.draw_char(screen_x, screen_y, char='.', fg=(c, c, c))

	def key(self, key):
		if key == 'UP' or key == 'k':
			self._view_centre[1] -= 1
			return True
		elif key == 'DOWN' or key == 'j':
			self._view_centre[1] += 1
			return True
		elif key == 'LEFT' or key == 'h':
			self._view_centre[0] -= 1
			return True
		elif key == 'RIGHT' or key == 'l':
			self._view_centre[0] += 1
			return True
		if key == 'shift+UP' or key == 'shift+k':
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

class MainView(ui.View):
	__slots__ = (
		'_display',
		'_game',
		'_top_bar_win',
		'_map_win'
	)

	def __init__(self, display, game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._top_bar_win = TopBarWin(game)
		view_centre = tuple(int(game.height.shape[i] / 2) for i in (1, 0))
		self._map_win = MapWin(game, view_centre)
		self.windows.add(self._top_bar_win)
		self.windows.add(self._map_win)
		self.on_resize.add(self.resize)
		self.on_key.add(self.key)

	def resize(self, dim):
		self._top_bar_win.place((0, 0), (dim[0], 1))
		self._map_win.place((0, 1), (dim[0], dim[1] - 1))

	def key(self, key):
		if key == 'q':
			self._display.quit()
			return True
