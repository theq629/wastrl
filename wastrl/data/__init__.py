class _HandlerCollection:
	__slots__ = (
		'_prepared',
		'_items'
	)

	def __init__(self):
		self._prepared = True
		self._items = []

	def add(self, x, priority=0):
		self._prepared = False
		self._items.append((priority, x))

	def handle(self, priority=0):
		def decorate(f):
			return self.add(f, priority=priority)
		return decorate

	def __len__(self):
		return len(self._items)

	def __iter__(self):
		if not self._prepared:
			self._prepare()
		return self._items.__iter__()

	def _prepare(self):
		self._items.sort()
		self._prepared = True

class Event:
	__slots__ = (
		'_init_value',
		'_fold_f',
		'_on'
	)

	def __init__(self, init_value=None, fold_f=lambda a, b: None):
		self._init_value = init_value
		self._fold_f = fold_f
		self._on = _HandlerCollection()

	@property
	def on(self):
		return self._on

	def trigger(self, *args, **kwargs):
		value = self._init_value
		for _, f in self._on:
			value = self._fold_f(value, f(*args, **kwargs))
		return value

class Property:
	__slots__ = (
		'_storage',
	)

	def __init__(self):
		self._storage = {}

	def __getitem__(self, key):
		return self._storage[key]

	def __setitem__(self, key, value):
		self._storage[key] = value

	def remove(self, key):
		del self._storage[key]

	def __len__(self):
		return len(self._storage)

	def keys(self):
		return self._storage.keys()

	def values(self):
		return self._storage.values()

	def items(self):
		return self._storage.items()

class Thing:
	_next_thing_index = 0

	__slots__ = (
		'_index',
	)

	def __init__(self):
		self._index = Thing._next_thing_index
		Thing._next_thing_index += 1

	@property
	def index(self):
		return self._index
