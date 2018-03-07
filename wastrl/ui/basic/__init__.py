import textwrap
from .. import Window, View
from . import commands
from . import colours

class KeyBindingsWindow(Window):
	__slots__ = (
		'_colours',
		'_key_event_sets',
		'_bindings',
		'_cache'
	)

	def __init__(self, key_event_sets, bindings, colours=colours, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._colours = colours
		self._key_event_sets = key_event_sets
		self._bindings = bindings
		self._cache = None
		self.on_redraw.add(self.redraw)

	def needed_dim_y(self, dim_x):
		return len(self._lines_for_width(dim_x))

	def redraw(self, console):
		lines = self._lines_for_width(self.dim[0])
		console.clear()
		for y, line in enumerate(lines):
			x = 1
			for command, keys in line:
				console.draw_str(x, y, string=command, fg=self._colours.action_command)
				x += len(command) + 1
				for i, key in enumerate(keys):
					console.draw_str(x, y, string=key, fg=self._colours.action_key)
					x += len(key)
					if i < len(keys) - 1:
						console.draw_char(x, y, char='/', fg=self._colours.action_sep)
					x += 1

	def _lines_for_width(self, dim_x):
		if self._cache is not None:
			cached_dim_x, lines = self._cache
			if cached_dim_x == dim_x:
				return lines
		lines = self._calc_lines_for_width(dim_x - 2)
		self._cache = (dim_x, lines)
		return lines

	def _calc_lines_for_width(self, dim_x):
		lines = [[]]
		space_left_on_line = dim_x
		for key_events in self._key_event_sets:
			for command in key_events:
				keys = self._bindings.inverse[command]
				total_len = len(command) + sum(len(k) for k in keys) + 1 + len(keys)
				if space_left_on_line < total_len:
					lines.append([])
					space_left_on_line = dim_x
				else:
					space_left_on_line -= total_len
				lines[-1].append((command, keys))
		return lines

class TextWindow(Window):
	__slots__ = (
		'_colours',
		'_title',
		'_text',
		'_title_lines',
		'_text_lines',
		'_last_draw_size',
		'_start_pos',
		'_page_size'
	)

	def __init__(self, title, text, commands=commands, colours=colours, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._colours = colours
		self._title = title
		self._text = text
		self._title_lines = None
		self._text_lines = None
		self._last_draw_size = None
		self._start_pos = 0
		self._page_size = 1
		self.on_redraw.add(self.redraw)
		self.setup_keys()

	def setup_keys(self):
		self.on_key[commands.line_up].add(lambda: self.move_page(-1))
		self.on_key[commands.line_down].add(lambda: self.move_page(1))
		self.on_key[commands.page_up].add(lambda: self.move_page(-self._page_size))
		self.on_key[commands.page_down].add(lambda: self.move_page(self._page_size))

	def move_page(self, diff):
		self._start_pos = max(0, min(len(self._text_lines) - self._page_size, self._start_pos + diff))

	def redraw(self, console):
		if self._last_draw_size is None or self._last_draw_size != self.dim:
			self._title_lines = textwrap.wrap(self._title, self.dim[0] - 1)
			self._text_lines = textwrap.wrap(self._text, self.dim[0] - 1)
			self._page_size = self.dim[1] - len(self._title_lines) - 3
			self._start_pos = max(0, min(len(self._text_lines) - self._page_size, self._start_pos))

		console.clear()
		y = 1

		for line in self._title_lines:
			console.draw_str(1, y, string=line, fg=self._colours.title)
			y += 1

		y += 1

		for line in self._text_lines[self._start_pos : self._start_pos + self._page_size]:
			console.draw_str(1, y, string=line, fg=self._colours.text)
			y += 1

class TextView(View):
	__slots__ = (
		'_max_text_width',
		'_text_win',
		'_keys_win'
	)

	def __init__(self, title, text, commands=commands, max_text_width=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._max_text_width = max_text_width
		self._text_win = TextWindow(title, text, keybindings=self.keybindings)
		self._keys_win = KeyBindingsWindow((self.on_key, self._text_win.on_key), self.keybindings)
		self.windows.add(self._text_win)
		self.windows.add(self._keys_win)
		self.on_resize.add(self.resize)
		self.on_key[commands.close].add(lambda: self.close())

	def resize(self, dim):
		text_win_dim_x = dim[0]
		if self._max_text_width is not None:
			text_win_dim_x = min(text_win_dim_x, self._max_text_width)
		text_width_margin_x = int((dim[0] - text_win_dim_x) / 2)

		keys_win_dim_y = self._keys_win.needed_dim_y(dim[0])

		self._text_win.place((text_width_margin_x, 0), (text_win_dim_x, dim[1] - keys_win_dim_y))
		self._keys_win.place((0, dim[1] - keys_win_dim_y), (dim[0], keys_win_dim_y))
