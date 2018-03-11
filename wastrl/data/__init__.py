import sys
import traceback
import collections

event_debug = False

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
		self._items.sort(key=lambda pf: pf[0])
		self._prepared = True

class Event:
	__slots__ = (
		'_init_value',
		'_fold_f',
		'_on',
		'_name',
		'debug'
	)

	def __init__(self, init_value=None, fold_f=lambda a, b: None, name=None, debug=True):
		self._init_value = init_value
		self._fold_f = fold_f
		self._on = _HandlerCollection()
		self._name = name
		self.debug = event_debug if debug is None else debug

	@property
	def on(self):
		return self._on

	def trigger(self, *args, **kwargs):
		global event_debug
		if self.debug and event_debug:
			name_str = "" if self._name is None else " " + self._name
			print(f"event{name_str}", args, kwargs, file=sys.stderr)
		value = self._init_value
		for _, f in self._on:
			try:
				value = self._fold_f(value, f(*args, **kwargs))
			except Exception as e:
				print("error in event:", file=sys.stderr)
				traceback.print_exc(file=sys.stderr)
		return value

class _AllProperties:
	__slots__ = (
		'_all',
	)

	def __init__(self):
		self._all = []

	def __iter__(self):
		return self._all.__iter__()

	def remove(self, thing):
		for property in self._all:
			if thing in property:
				property.remove(thing)

	def clear(self):
		for property in self._all:
			property.clear()

class BaseProperty:
	all = _AllProperties()

	def __init__(self):
		BaseProperty.all._all.append(self)

class ValuedProperty(BaseProperty):
	__slots__ = (
		'_storage',
	)

	def __init__(self):
		super().__init__()
		self._storage = {}

	def __getitem__(self, key):
		return self._storage[key]

	def __setitem__(self, key, value):
		self._storage[key] = value

	def remove(self, key):
		del self._storage[key]

	def __len__(self):
		return len(self._storage)

	def __contains__(self, key):
		return key in self._storage

	def keys(self):
		return self._storage.keys()

	def values(self):
		return self._storage.values()

	def items(self):
		return self._storage.items()

	def __iter__(self):
		return self._storage.__iter__()

	def clear(self):
		self._storage.clear()

	def join_keys(self, *others):
		for key, value in self._storage.items():
			try:
				yield (key, value) + tuple(other[key] for other in others)
			except KeyError:
				pass

	def join_values(self, *others):
		for key, value in self._storage.items():
			try:
				yield (key, value) + tuple(other[value] for other in others)
			except KeyError:
				pass

class SetProperty(BaseProperty):
	__slots__ = (
		'_storage',
	)

	def __init__(self):
		super().__init__()
		self._storage = set()

	def __len__(self):
		return len(self._storage)

	def __contains__(self, key):
		return key in self._storage

	def add(self, key):
		return self._storage.add(key)

	def remove(self, key):
		return self._storage.remove(key)

	def __iter__(self):
		return self._storage.__iter__()

	def clear(self):
		self._storage.clear()

	def join(self, *others):
		for key in self._storage:
			try:
				yield (key,) + tuple(other[key] for other in others)
			except KeyError:
				pass

class OrderedSetProperty(BaseProperty):
	__slots__ = (
		'_storage',
	)

	def __init__(self):
		super().__init__()
		self._storage = collections.OrderedDict()

	def __len__(self):
		return len(self._storage)

	def __contains__(self, key):
		return key in self._storage

	def add(self, key):
		self._storage[key] = None

	def remove(self, key):
		del self._storage[key]

	def __iter__(self):
		return iter(self._storage.keys())

	def clear(self):
		self._storage.clear()

	def join(self, *others):
		for key in self._storage.keys():
			try:
				yield (key,) + tuple(other[key] for other in others)
			except KeyError:
				pass

_next_thing_index = 0

def Thing(setup={}):
	global _next_thing_index
	thing = _next_thing_index
	_next_thing_index += 1
	for property, value in setup.items():
		if hasattr(property, '__setitem__'):
			property[thing] = value
		elif value:
			property.add(thing)
	return thing

def reset():
	BaseProperty.all.clear()
	Thing._next_thing_index = 0
