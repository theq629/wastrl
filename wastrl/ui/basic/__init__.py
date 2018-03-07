import textwrap
import abc
import math
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

class PaginatedWindow(Window, abc.ABC):
	__slots__ = (
		'_colours',
		'_title',
		'_title_lines',
		'_value',
		'_prepared_value',
		'_total_lines',
		'_last_prepare_size',
		'_page_size',
		'_start_pos'
	)

	def __init__(self, title, value, commands=commands, colours=colours, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._colours = colours
		self._title = title
		self._value = value
		self._title_lines = None
		self._prepared_value = None
		self._last_prepare_size = None
		self._total_lines = 0
		self._start_pos = 0
		self._page_size = 1
		self.setup_keys()
		self.on_redraw.add(self._redraw_base)

	@property
	def num_title_lines(self):
		return len(self._title_lines)

	@property
	def start_pos(self):
		return self._start_pos

	@property
	def page_size(self):
		return self._page_size

	@property
	def prepared(self):
		if self._last_prepare_size is None or self._last_prepare_size != self.dim:
			self._title_lines = textwrap.wrap(self._title, self.dim[0] - 1)
			self._page_size = self.dim[1] - len(self._title_lines) - 3
			self._prepared_value, self._total_lines = self.prepare(self._value)
			self._last_prepare_size = self.dim
		return self._prepared_value

	@abc.abstractmethod
	def prepare(self, value):
		raise NotImplementedError()

	def setup_keys(self):
		self.on_key[commands.line_up].add(lambda: self._move_page(-1))
		self.on_key[commands.line_down].add(lambda: self._move_page(1))
		self.on_key[commands.page_up].add(lambda: self._move_page(-self._page_size))
		self.on_key[commands.page_down].add(lambda: self._move_page(self._page_size))

	def _move_page(self, diff):
		self._start_pos = max(0, min(self._total_lines - self._page_size, self._start_pos + diff))

	def _redraw_base(self, console):
		self.prepared
		console.clear()
		y = 1
		for line in self._title_lines:
			console.draw_str(1, y, string=line, fg=self._colours.title)
			y += 1

class TextWindow(PaginatedWindow):
	def __init__(self, title, text, commands=commands, colours=colours, *args, **kwargs):
		super().__init__(title, text, *args, **kwargs)
		self.on_redraw.add(self.redraw)

	def prepare(self, text):
		text_lines = textwrap.wrap(text, self.dim[0] - 2)
		return text_lines, len(text_lines)

	def redraw(self, console):
		text_lines = self.prepared
		y = self.num_title_lines + 2
		for line in text_lines[self.start_pos : self.start_pos + self.page_size]:
			console.draw_str(1, y, string=line, fg=self._colours.text)
			y += 1

class MenuWindow(PaginatedWindow):
	def __init__(self, title, items, commands=commands, colours=colours, *args, **kwargs):
		super().__init__(title, items, *args, **kwargs)
		self.on_redraw.add(self.redraw)

	def prepare(self, items):
		max_key_width = max(len(k) for k, t in items) if len(items) > 0 else 0
		prepared = tuple((k, textwrap.wrap(t, self.dim[0] - max_key_width - 3)) for k, t in items)
		return prepared, sum(len(ls) for k, ls in prepared)

	def redraw(self, console):
		prepared = self.prepared
		max_key_len = max(len(k) for k, ls in prepared) if len(prepared) > 0 else 0

		def find_start_pos():
			pos = item_i = line_i = 0
			while item_i < len(prepared):
				while line_i < len(prepared):
					key, lines = prepared[item_i]
					pos += 1
					if pos >= self.start_pos:
						return item_i, line_i
					line_i += 1
				item_i += i
				line_i = 0
			return item_i, line_i
		item_i, line_i = find_start_pos()

		y = self.num_title_lines + 2
		while item_i < len(prepared):
			key, lines = prepared[item_i]
			while line_i < len(lines):
				if line_i == 0:
					console.draw_str(1, y, string=key, fg=self._colours.menu_key)
				console.draw_str(max_key_len + 2, y, string=lines[line_i], fg=self._colours.text)
				line_i += 1
			item_i += 1
			line_i = 0
			y += 1

class ViewWithKeys(View):
	__slots__ = (
		'_max_width',
		'_main_win',
		'_keys_win'
	)

	def __init__(self, title, value, win_maker, commands=commands, max_width=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._max_width = max_width
		self._main_win = win_maker(title, value, keybindings=self.keybindings)
		self._keys_win = KeyBindingsWindow((self.on_key, self._main_win.on_key), self.keybindings)
		self.windows.add(self._main_win)
		self.windows.add(self._keys_win)
		self.on_resize.add(self.resize)
		self.on_key[commands.close].add(lambda: self.close())

	def resize(self, dim):
		main_win_dim_x = dim[0]
		if self._max_width is not None:
			main_win_dim_x = min(main_win_dim_x, self._max_width)
		text_width_margin_x = int((dim[0] - main_win_dim_x) / 2)

		keys_win_dim_y = self._keys_win.needed_dim_y(dim[0])

		self._main_win.place((text_width_margin_x, 0), (main_win_dim_x, dim[1] - keys_win_dim_y))
		self._keys_win.place((0, dim[1] - keys_win_dim_y), (dim[0], keys_win_dim_y))
