from . import ui

def int_pair(s):
	x, y = s.split(',')
	return (int(x), int(y))

class TopBar(ui.Window):
	__slots__ = ()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.on_redraw.add(self.redraw)

	def redraw(self, console):
		console.draw_char(0, 0, '@')

class MainView(ui.View):
	__slots__ = (
		'_display',
		'_top_bar'
	)

	def __init__(self, display, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._top_bar = TopBar()
		self.windows.add(self._top_bar)
		self.on_resize.add(self.resize)
		self.on_key.add(self.key)

	def resize(self, dim):
		self._top_bar.place((0, 0), (dim[0], 1))

	def key(self, key):
		if key == 'q':
			self._display.quit()
			return True
		elif key == 'UP':
			return True
		elif key == 'DOWN':
			return True
		elif key == 'LEFT':
			return True
		elif key == 'RIGHT':
			return True

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Wastrl")
	parser.add_argument('-r', '--resolution', metavar="X,Y",
		dest = "resolution", type = int_pair, default = (80, 50),
		help = "Resolution of display in characters."
	)
	parser.add_argument('-f', '--fullscreen',
		dest = "fullscreen", default = False, action = 'store_true',
		help = "Use fullscreen display."
	)
	args = parser.parse_args()

	with ui.Display(screen_dim=args.resolution, fullscreen=args.fullscreen, title="Wastrl") as disp:
		disp.views.add(MainView(disp))
