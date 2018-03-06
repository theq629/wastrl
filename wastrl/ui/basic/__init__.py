import textwrap
from .. import Window, View
from . import commands
from . import colours

class TextWindow(Window):
	__slots__ = (
		'_colours',
		'_title',
		'_text',
		'_title_lines',
		'_text_lines',
		'_last_draw_size'
	)

	def __init__(self, title, text, commands=commands, colours=colours, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._colours = colours
		self._title = title
		self._text = text
		self._title_lines = None
		self._text_lines = None
		self._last_draw_size = None
		self.on_redraw.add(self.redraw)

	def redraw(self, console):
		if self._last_draw_size is None or self._last_draw_size != self.dim:
			self._title_lines = textwrap.wrap(self._title, self.dim[0] - 1)
			self._text_lines = textwrap.wrap(self._text, self.dim[0] - 1)

		y = 1
		console.clear()

		for line in self._title_lines:
			console.draw_str(1, y, string=line, fg=self._colours.title)
			y += 1

		y += 1

		for line in self._text_lines:
			console.draw_str(1, y, string=line, fg=self._colours.text)
			y += 1

class TextView(View):
	__slots__ = (
		'_text_win',
	)

	def __init__(self, title, text, commands=commands, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._text_win = TextWindow(title, text)
		self.windows.add(self._text_win)
		self.on_resize.add(self.resize)
		self.on_key[commands.close].add(lambda: self.close())

	def resize(self, dim):
		self._text_win.place((0, 0), dim)
