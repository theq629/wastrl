import configparser

class UnknownSection(Exception):
	pass

class UnknownKey(Exception):
	pass

class UnknownCommand(Exception):
	pass

class KeyBindingsInverse:
	__slots__ = (
		'_storage',
	)

	def __init__(self):
		self._storage = {}

	def __getitem__(self, command):
		return self._storage[command]

	def get(self, command):
		return self._storage.get(command)

class KeyBindings:
	__slots__ = (
		'_storage',
		'_inverse'
	)

	def __init__(self):
		self._storage = {}
		self._inverse = KeyBindingsInverse()

	def __getitem__(self, key):
		return self._storage[key]

	def get(self, key):
		return self._storage.get(key)

	@property
	def inverse(self):
		return self._inverse

	def _set(self, storage):
		self._storage = storage
		self._inverse._storage = {}
		for key, command in self._storage.items():
			self._inverse._storage.setdefault(command, ())
			self._inverse._storage[command] += (key,)

class CompoundKeybindings:
	__slots__ = (
		'_cfgparser',
		'_bindings'
	)

	def __init__(self, sections):
		self._cfgparser = configparser.ConfigParser()
		self._bindings = dict((s, KeyBindings()) for s in sections)

	def __getitem__(self, section):
		return self._bindings[section]

	def get(self, section):
		return self._bindings.get(section)

	def load(self, path):
		self._cfgparser = configparser.ConfigParser()
		self._cfgparser.read(path)
		for section in self._bindings.keys():
			self._bindings[section]._set(self._cfgparser[section] if section in self._cfgparser else {})

	def save(self, path):
		with open(path, 'w') as file:
			self._cfgparser.write(file)

	def verify(self, sections=None, keys=None, commands=None):
		if sections is None:
			sections = set(self._bindings.keys())
		for section in self._cfgparser.sections():
			if section not in sections:
				raise UnknownSection(section)
		if keys is not None:
			for section in self._cfgparser.sections():
				for key in self._cfgparser[section].keys():
					if key not in keys:
						raise UnknownKey(key)
		if commands is not None:
			for section in self._cfgparser.sections():
				for command in self._cfgparser[section].values():
					if command not in commands:
						raise UnknownCommand(command)
