import collections
import textwrap
import abc
import math
from .. import Window, View
from . import commands

Colours = collections.namedtuple('Colours', (
	'background',
	'title',
	'text',
	'menu_key',
	'menu_key_sel',
	'action_command',
	'action_key',
	'action_sep',
	'keys_background'
))

default_colours = Colours(
	background = 0x000000,
	title = 0xffcf6d,
	text = 0xcfc19a,
	menu_key = 0x10ad80,
	menu_key_sel = 0xffcf6d,
	action_command = 0x10ad80,
	action_key = 0xffcf6d,
	action_sep = 0x10ad80,
	keys_background = 0x222222
)

class KeyBindingsWindow(Window):
	__slots__ = (
		'_colours',
		'_key_event_sets',
		'_bindings',
		'_cache'
	)

	def __init__(self, key_event_sets, bindings, colours=default_colours, *args, **kwargs):
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
		console.clear(bg=self._colours.keys_background)
		for y, line in enumerate(lines):
			x = 1
			for command, keys in line:
				console.draw_str(x, y, string=command, fg=self._colours.action_command, bg=self._colours.keys_background)
				x += len(command) + 1
				for i, key in enumerate(keys):
					console.draw_str(x, y, string=key, fg=self._colours.action_key, bg=self._colours.keys_background)
					x += len(key)
					if i < len(keys) - 1:
						console.draw_char(x, y, char='/', fg=self._colours.action_sep, bg=self._colours.keys_background)
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
				keys = tuple(self.name_key(k) for k in self._bindings.inverse[command])
				command = self.name_command(command)
				total_len = len(command) + sum(len(k) for k in keys) + 1 + len(keys)
				if space_left_on_line < total_len:
					lines.append([])
					space_left_on_line = dim_x
				else:
					space_left_on_line -= total_len
				lines[-1].append((command, keys))
		return lines

	def name_command(self, command):
		return command.replace('_', ' ')

	def name_key(self, key):
		return key

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

	def __init__(self, title=None, value="", commands=commands, colours=default_colours, do_keys=True, *args, **kwargs):
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
		if do_keys:
			self.setup_keys()
		self.on_redraw.add(self._redraw_base)

	@property
	def num_title_lines(self):
		return len(self._title_lines) if self._title_lines is not None else 0

	@property
	def start_pos(self):
		return self._start_pos

	@property
	def page_size(self):
		return self._page_size

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, value):
		self._value = value
		self._last_prepare_size = None
		self.prepared

	@property
	def prepared(self):
		if self._last_prepare_size is None or self._last_prepare_size != self.dim:
			self._title_lines = textwrap.wrap(self._title, self.dim[0] - 1) if self._title is not None else None
			self._page_size = self.dim[1] - self.num_title_lines - 3
			self._prepared_value, self._total_lines = self.prepare(self._value)
			self._last_prepare_size = self.dim
		return self._prepared_value

	@abc.abstractmethod
	def prepare(self, value):
		raise NotImplementedError()

	def scroll_to_start(self):
		self._start_pos = 0

	def scroll_to_end(self):
		self._start_pos = max(0, self._total_lines - self._page_size)

	def setup_keys(self):
		self.on_key[commands.line_up].add(lambda: self._move_page(-1))
		self.on_key[commands.line_down].add(lambda: self._move_page(1))
		self.on_key[commands.page_up].add(lambda: self._move_page(-self._page_size))
		self.on_key[commands.page_down].add(lambda: self._move_page(self._page_size))

	def _move_page(self, diff):
		self._start_pos = max(0, min(self._total_lines - self._page_size, self._start_pos + diff))

	def _redraw_base(self, console):
		self.prepared
		console.clear(bg=self._colours.background)
		if self._title_lines is not None:
			y = 1
			for line in self._title_lines:
				console.draw_str(1, y, string=line, fg=self._colours.title, bg=self._colours.background)

class TextWindow(PaginatedWindow):
	def __init__(self, title=None, text="", commands=commands, colours=default_colours, *args, **kwargs):
		super().__init__(title, text, colours=colours, *args, **kwargs)
		self.on_redraw.add(self.redraw)

	def prepare(self, text):
		text_lines = tuple(l for l0 in text.split("\n") for l in (textwrap.wrap(l0, self.dim[0] - 2, replace_whitespace=False) if len(l0) > 0 else (l0,)))
		return text_lines, len(text_lines)

	def redraw(self, console):
		text_lines = self.prepared
		y = self.num_title_lines + 2
		for line in text_lines[self.start_pos : self.start_pos + self.page_size]:
			console.draw_str(1, y, string=line, fg=self._colours.text, bg=self._colours.background)
			y += 1

def is_printable_char(char):
	if len(char) == 1:
		c = ord(char)
		return 0x20 <= c <= 0x7E
	return False

class TextEnterWindow(TextWindow):
	__slots__ = (
		'_allow_key',
	)

	def __init__(self, title=None, text="", allow_keys=is_printable_char, commands=commands, colours=default_colours, *args, **kwargs):
		super().__init__(title, text, colours=colours, *args, **kwargs)
		self._allow_key = allow_keys
		self.on_key.on_other.add(self.handle_other_key)

	def handle_other_key(self, key):
		if self._allow_key(key):
			self.value += key

class MenuWindow(PaginatedWindow):
	__slots__ = (
		'_item_keys',
		'_auto_close_view'
		'_select_handler',
		'_select_multi',
		'_selection'
	)

	def __init__(self, title, items, select_handler=None, select_multi=False, commands=commands, colours=default_colours, auto_close_view=True, *args, **kwargs):
		super().__init__(title, items, *args, **kwargs)
		self._item_keys = set(k for k, v in items)
		self._auto_close_view = auto_close_view
		self._select_handler = select_handler
		self._select_multi = select_multi
		self._selection = set()
		self.on_redraw.add(self.redraw)
		self.on_key[commands.select_all].add(self.select_all)
		if select_handler is not None:
			if select_multi:
				self.on_key.on_other.add(self.handle_other_key_select_multi)
				self.on_close.add(self.handle_close_select_multi)
			else:
				self.on_key.on_other.add(self.handle_other_key_select_single)

	def handle_other_key_select_single(self, key):
		if key in self._item_keys:
			self._select_handler(key)
			if self._auto_close_view:
				self.view.close()
			return True

	def handle_other_key_select_multi(self, key):
		if key in self._item_keys:
			if key in self._selection:
				self._selection.remove(key)
			else:
				self._selection.add(key)
			return True

	def handle_close_select_multi(self):
		self._select_handler(self._selection)

	def select_all(self):
		if len(self._selection) == len(self._item_keys):
			self._selection.clear()
		else:
			self._selection = set(self._item_keys)

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
					fg = self._colours.menu_key if key not in self._selection else self._colours.menu_key_sel
					console.draw_str(1, y, string=key, fg=fg, bg=self._colours.background)
				console.draw_str(max_key_len + 2, y, string=lines[line_i], fg=self._colours.text, bg=self._colours.background)
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

	@property
	def window(self):
		return self._main_win

	def resize(self, dim):
		main_win_dim_x = dim[0]
		if self._max_width is not None:
			main_win_dim_x = min(main_win_dim_x, self._max_width)
		text_width_margin_x = int((dim[0] - main_win_dim_x) / 2)

		keys_win_dim_y = self._keys_win.needed_dim_y(dim[0])

		self._main_win.place((text_width_margin_x, 0), (main_win_dim_x, dim[1] - keys_win_dim_y))
		self._keys_win.place((0, dim[1] - keys_win_dim_y), (dim[0], keys_win_dim_y))

class LoadingView(View):
	__slots__ = (
		'_text_win',
		'_max_width'
	)

	def __init__(self, title, text, max_width=80, **kwargs):
		super().__init__(**kwargs)
		self._text_win = TextWindow(title=title, text=text)
		self._max_width = max_width
		self.windows.add(self._text_win)
		self.on_resize.add(self.resize)

	def resize(self, dim):
		main_win_dim_x = dim[0]
		if self._max_width is not None:
			main_win_dim_x = min(main_win_dim_x, self._max_width)
		text_width_margin_x = int((dim[0] - main_win_dim_x) / 2)
		self._text_win.place((text_width_margin_x, 0), (main_win_dim_x, dim[1]))
