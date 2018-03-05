import tdl

class ControlledCollection:
	__slots__ = (
		'_items',
	)

	def __init__(self):
		self._items = []

	def add(self, x):
		self._items.append(x)

	def __len__(self):
		return len(self._items)

	def __iter__(self):
		return self._items.__iter__()

class EventHandler(ControlledCollection):
	def _trigger(self, *args, **kwargs):
		for f in self:
			if f(*args, **kwargs):
				return True
		return False

class Window:
	__slots__ = (
		'_pos',
		'_dim',
		'_console',
		'_on_redraw',
		'_on_key'
	)

	def __init__(self, pos=(0, 0), dim=(0, 0)):
		self.place(pos, dim)
		self._on_redraw = EventHandler()
		self._on_key = EventHandler()

	@property
	def pos(self):
		return self._pos

	@property
	def dim(self):
		return self._dim

	@property
	def on_redraw(self):
		return self._on_redraw

	@property
	def on_key(self):
		return self._on_key

	def place(self, pos, dim):
		self._pos = pos
		self._dim = dim
		self._console = tdl.Console(*dim) if self._dim != (0, 0) else None

	def _draw(self, dest_con):
		if self._console is not None:
			self._on_redraw._trigger(self._console)
			dest_con.blit(self._console, self._pos[0], self._pos[1], self._dim[0], self._dim[1], 0, 0)

class View:
	__slots__ = (
		'_windows',
		'_console',
		'_on_resize',
		'_on_key'
	)

	def __init__(self):
		self._windows = ControlledCollection()
		self._console = None
		self._on_resize = EventHandler()
		self._on_key = EventHandler()
		self._on_resize.add(self._resize)
		self._resize((0, 0))

	@property
	def windows(self):
		return self._windows

	@property
	def on_resize(self):
		return self._on_resize

	@property
	def on_key(self):
		return self._on_key

	def add(self, window):
		self._windows.append(window)

	def _tdl_event(self, event):
		if event.type == 'KEYDOWN' and event.key != 'TEXT':
			key_name = event.char if event.key == 'CHAR' else event.key
			if event.shift:
				key_name = "shift+" + key_name
			if self._on_key._trigger(key_name):
				return True
			else:
				for win in self._windows:
					if win._on_key._trigger(key_name):
						return True
			return False

	def _resize(self, dim):
		self._console = tdl.Console(*dim) if dim != (0, 0) else None

	def _draw(self, dest_con):
		if self._console is not None:
			for win in self._windows:
				win._draw(self._console)
			dest_con.blit(self._console, 0, 0, self._console.width, self._console.height, 0, 0)

class Display:
	__slots__ = (
		'_dim',
		'_tdl_opts',
		'_root_console',
		'_views',
		'_running'
	)

	def __init__(self, screen_dim, fullscreen=False, title=None):
		self._dim = screen_dim
		self._tdl_opts = {
			'fullscreen': fullscreen,
			'title': title
		}
		self._root_console = None
		self._views = ControlledCollection()
		self._running = False

	@property
	def views(self):
		return self._views

	def run(self):
		self._running = True
		self._setup()
		self._draw()
		while self._running:
			if self._handle_events():
				self._draw()

	def close(self):
		pass

	def quit(self):
		self._running = False

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		if type is not None:
			self.close()
			return
		else:
			try:
				self.run()
			finally:
				self.close()

	def _setup(self):
		self._root_console = tdl.init(*self._dim, **self._tdl_opts)
		for view in self._views:
			view._on_resize._trigger(self._dim)

	def _handle_events(self):
		if tdl.event.is_window_closed():
			self.quit()
			return
		for event in tdl.event.get():
			for view in self._views:
				if view._tdl_event(event):
					return True
		return False

	def _draw(self):
		for view in self._views:
			view._draw(self._root_console)
		tdl.flush()
