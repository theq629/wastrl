import configparser

class UnknownSection(Exception):
	pass

class UnknownKey(Exception):
	pass

class UnknownCommand(Exception):
	pass

def verify(keybindings, sections=None, keys=None, commands=None):
	if sections is not None:
		for section in keybindings.sections():
			if section not in sections:
				raise UnknownSection(section)
	if keys is not None:
		for section in keybindings.sections():
			for key in keybindings[section].keys():
				if key not in keys:
					raise UnknownKey(key)
	if commands is not None:
		for section in keybindings.sections():
			for command in keybindings[section].values():
				if command not in commands:
					raise UnknownCommand(command)

def load(path):
	keybindings = configparser.ConfigParser()
	keybindings.read(path)
	return keybindings

def save(path, keymap):
		keybindings = configparser.ConfigParser()
		with open(path, 'w') as file:
			keybindings.write(file)
