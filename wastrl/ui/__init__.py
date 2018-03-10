import tdl

class _ControlledCollection:
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

	def _remove(self, x):
		self._items.remove(x)

class EventHandler(_ControlledCollection):
	def _trigger(self, *args, **kwargs):
		for f in self:
			if f(*args, **kwargs):
				return True
		return False

class PartedEventHandler:
	__slots__ = (
		'_parts',
	)

	def __init__(self):
		self._parts = {}

	def __contains__(self, part):
		return part in self._parts

	def __getitem__(self, part):
		if part not in self._parts:
			self._parts[part] = EventHandler()
		return self._parts[part]

	def __iter__(self):
		return self._parts.__iter__()

	def _trigger(self, *args, **kwargs):
		part, args, kwargs = self._map_input(*args, **kwargs)
		if part in self._parts:
			self._parts[part]._trigger(*args, **kwargs)
			return True

	def _map_input(self, *args, **kwargs):
		raise NotImplementedError()

class KeyEventHandler(PartedEventHandler):
	__slots__ = (
		'_keybindings',
		'_on_other'
	)

	def __init__(self, keybindings):
		super().__init__()
		self._keybindings = keybindings
		self._on_other = EventHandler()

	@property
	def on_other(self):
		return self._on_other

	def _map_input(self, key, *args, **kwargs):
		return self._keybindings.get(key), args, kwargs

	def _trigger(self, key, *args, **kwargs):
		if not super()._trigger(key, *args, **kwargs):
			self._on_other._trigger(key, *args, **kwargs)

class Window:
	__slots__ = (
		'_view',
		'_pos',
		'_dim',
		'_console',
		'_keybindings',
		'_on_frame',
		'_on_redraw',
		'_on_close',
		'_on_key',
		'_on_click'
	)

	def __init__(self, pos=(0, 0), dim=(0, 0), keybindings={}):
		self._view = None
		self.place(pos, dim)
		self._keybindings = keybindings
		self._on_frame = EventHandler()
		self._on_redraw = EventHandler()
		self._on_close = EventHandler()
		self._on_key = KeyEventHandler(keybindings)
		self._on_click = KeyEventHandler(keybindings)

	@property
	def view(self):
		return self._view

	@property
	def pos(self):
		return self._pos

	@property
	def dim(self):
		return self._dim

	@property
	def keybindings(self):
		return self._keybindings

	@property
	def on_frame(self):
		return self._on_frame

	@property
	def on_redraw(self):
		return self._on_redraw

	@property
	def on_close(self):
		return self._on_close

	@property
	def on_key(self):
		return self._on_key

	@property
	def on_click(self):
		return self._on_click

	def place(self, pos, dim):
		self._pos = pos
		self._dim = dim
		self._console = tdl.Console(*dim) if self._dim != (0, 0) else None

	def _draw(self, dest_con):
		if self._console is not None:
			self._on_redraw._trigger(self._console)
			dest_con.blit(self._console, self._pos[0], self._pos[1], self._dim[0], self._dim[1], 0, 0)

	def redraw(self):
		if self._view is not None:
			self._view.redraw()

class _WindowCollection(_ControlledCollection):
	__slots__ = (
		'_view',
	)

	def __init__(self, view):
		super().__init__()
		self._view = view

	def add(self, win):
		super().add(win)
		win._view = self._view

	def _remove(self, win):
		super()._remove(win)
		win._view = None

class View:
	__slots__ = (
		'_displays',
		'_windows',
		'_console',
		'_keybindings',
		'_open',
		'_on_frame',
		'_on_resize',
		'_on_close',
		'_on_key',
		'_on_click',
		'_on_before_redraw',
		'_on_after_redraw'
	)

	def __init__(self, keybindings={}):
		self._displays = []
		self._windows = _WindowCollection(self)
		self._console = None
		self._keybindings = keybindings
		self._open = True
		self._on_frame = EventHandler()
		self._on_resize = EventHandler()
		self._on_key = KeyEventHandler(keybindings)
		self._on_click = KeyEventHandler(keybindings)
		self._on_close = EventHandler()
		self._on_before_redraw = EventHandler()
		self._on_after_redraw = EventHandler()
		self._on_resize.add(self._resize)
		self._resize((0, 0))

	@property
	def windows(self):
		return self._windows

	@property
	def keybindings(self):
		return self._keybindings

	@property
	def on_frame(self):
		return self._on_frame

	@property
	def on_resize(self):
		return self._on_resize

	@property
	def on_close(self):
		return self._on_close

	@property
	def on_key(self):
		return self._on_key

	@property
	def on_click(self):
		return self._on_click

	@property
	def on_before_redraw(self):
		return self._on_before_redraw

	@property
	def on_after_redraw(self):
		return self._on_after_redraw

	def close(self):
		for win in self._windows:
			win._on_close._trigger()
		self._on_close._trigger()
		self._open = False
		for display in self._displays:
			display._views._remove(self)
		self._displays = []

	def _handle_frame(self):
		result = self.on_frame._trigger()
		for win in self._windows:
			result |= win._on_frame._trigger()
		return result

	def _tdl_event(self, event):
		if event.type == 'KEYDOWN' and event.key != 'TEXT':
			key_name = event.char if event.key == 'CHAR' else event.key
			if event.shift:
				key_name = "shift+" + key_name
			if event.control:
				key_name = "control+" + key_name
			if event.alt:
				key_name = "alt+" + key_name
			if event.meta:
				key_name = "meta+" + key_name
			if not self._on_key._trigger(key_name):
				for win in self._windows:
					if win._on_key._trigger(key_name):
						break
			return True
		elif event.type == 'MOUSEUP':
			key_name = "mouse+" + event.button
			if not self._on_click._trigger(key_name, event.cell):
				for win in self._windows:
					pos = tuple(event.cell[i] - win.pos[i] for i in range(2))
					if all(pos[i] >= 0 and pos[i] < win.dim[i] for i in range(2)):
						if win._on_click._trigger(key_name, pos):
							break
			return True
		return False

	def _resize(self, dim):
		self._console = tdl.Console(*dim) if dim != (0, 0) else None

	def _draw(self, dest_con):
		self._on_before_redraw._trigger()
		if self._open:
			if self._console is not None:
				for win in self._windows:
					win._draw(self._console)
				dest_con.blit(self._console, 0, 0, self._console.width, self._console.height, 0, 0)
			self._on_after_redraw._trigger()

	def redraw(self):
		for display in self._displays:
			display.redraw()

class _ViewCollection(_ControlledCollection):
	__slots__ = (
		'_display',
	)

	def __init__(self, display):
		super().__init__()
		self._display = display

	def add(self, view):
		super().add(view)
		view._displays.append(self._display)
		if self._display._running:
			view._on_resize._trigger(self._display._dim)
			self._display._draw()

	def _remove(self, view):
		super()._remove(view)
		view._displays.remove(self._display)
		if self._display._running:
			self._display._draw()
			if len(self) == 0:
				self._display.quit()

class Display:
	__slots__ = (
		'_dim',
		'_tdl_font_opts',
		'_tdl_opts',
		'_root_console',
		'_views',
		'_running'
	)

	def __init__(self, screen_dim, fullscreen=False, title=None, font_opts=None):
		self._dim = screen_dim
		self._tdl_font_opts = font_opts
		self._tdl_opts = {
			'fullscreen': fullscreen,
			'title': title
		}
		self._root_console = None
		self._views = _ViewCollection(self)
		self._running = False

	@property
	def views(self):
		return self._views

	def run(self):
		self._running = True
		self._setup()
		self._draw()
		while self._running:
			if self._handle_frame() or self._handle_events():
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
		if self._tdl_font_opts is not None and len(self._tdl_font_opts) > 0:
			tdl.set_font(**self._tdl_font_opts)
		self._root_console = tdl.init(*self._dim, **self._tdl_opts)
		for view in self._views:
			view._on_resize._trigger(self._dim)

	def _handle_frame(self):
		result = False
		for view in reversed(self._views._items):
			result |= view._handle_frame()
		return result

	def _handle_events(self):
		if tdl.event.is_window_closed():
			self.quit()
			return
		for event in tdl.event.get():
			for view in reversed(self._views._items):
				if view._tdl_event(event):
					return True
		return False

	def _draw(self):
		for view in self._views:
			view._draw(self._root_console)
		tdl.flush()

	def redraw(self):
		self._draw()
