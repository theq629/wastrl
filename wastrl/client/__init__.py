import os
import sys
import time
import pkg_resources
import appdirs
import configparser
from .. import ui
from ..ui import basic as basic_ui
from ..ui import keys
from .. import game
from .. import data
from . import main_view
from . import menu
from . import commands
from . import texts

prog_name = "wastrl"
prog_author = "theq629"

def int_pair(s):
	x, y = s.split(',')
	return (int(x), int(y))

def get_config_file_path(name, file_name):
	path = os.path.join(appdirs.user_config_dir(prog_name, prog_author), name)
	if not os.path.exists(path):
		path = pkg_resources.resource_filename(prog_name, os.path.join("config", name))
	if not os.path.exists(path):
		print(f"error: {file_name} config file does not exist: {path}", file=sys.stderr)
		sys.exit(1)
	else:
		print(f"{file_name} config file: {path}", file=sys.stderr)
	return path

def load_config():
	sections = { "display", "tdl_font", "ui", "debug" }
	path = get_config_file_path("config", "main")

	parser = configparser.ConfigParser()
	parser.read(path)

	for section in sections:
		if section not in parser:
			parser[section] = {}

	return parser

def load_keys():
	sections = { "main", "dialogs" }
	path = get_config_file_path("keys", "keys")

	keybindings = keys.CompoundKeybindings(sections)
	keybindings.load(path)
	try:
		keybindings.verify(sections=sections, commands=dir(commands))
	except keys.UnknownSection as e:
		print(f"warning: unknown section in keys file: {e}", file=sys.stderr)
	except keys.UnknownKey as e:
		print(f"warning: unknown key in keys file: {e}", file=sys.stderr)
	except keys.UnknownCommand as e:
		print(f"warning: unknown command in keys file: {e}", file=sys.stderr)
	return keybindings

def normalize_display_opts(opts):
	norm_opts = {}
	for key in { 'width', 'height' }:
		if key in opts:
			norm_opts[key] = int(opts[key])
	for key in { 'fullscreen' }:
		if key in opts:
			norm_opts[key] = opts.getboolean(key.lower())
	return norm_opts

def normalize_font_opts(opts):
	norm_opts = {}
	if 'path' in opts:
		path = os.path.expanduser(opts['path'])
		if len(os.path.split(path)[0]) == 0:
			path = pkg_resources.resource_filename(prog_name, os.path.join("resources", "fonts", path))
		norm_opts['path'] = path
	for key in { 'columns', 'rows' }:
		if key in opts:
			norm_opts[key] = int(opts[key])
	for key in { 'greyscale', 'columnFirst', 'altLayout' }:
		if key in opts:
			norm_opts[key] = opts.getboolean(key.lower())
	return norm_opts

def normalize_ui_opts(opts):
	norm_opts = {}
	if 'dialog_max_width' in opts:
		norm_opts['dialog_max_width'] = int(opts['dialog_max_width'])
	else:
		norm_opts['dialog_max_width'] = 80
	if 'status_bar_width' in opts:
		norm_opts['status_bar_width'] = int(opts['status_bar_width'])
	return norm_opts

def normalize_debug_opts(opts):
	norm_opts = {}
	norm_opts['log_events'] = opts.getboolean('log_events')
	norm_opts['ignore_fov'] = opts.getboolean('ignore_fov')
	norm_opts['starter_kit'] = opts.getboolean('starter_kit')
	return norm_opts

def normalize_config(config):
	config = dict(config)
	changes = (
		('display', normalize_display_opts),
		('tdl_font', normalize_font_opts),
		('ui', normalize_ui_opts),
		('debug', normalize_debug_opts)
	)
	for key, changer in changes:
		config[key] = changer(config[key])
	return config

def main():
	import argparse

	parser = argparse.ArgumentParser(description="Wastrl")
	parser.add_argument('-r', '--resolution', metavar="X,Y",
		dest = "resolution", type = int_pair, default = None,
		help = "Resolution of display in characters."
	)
	parser.add_argument('-f', '--fullscreen',
		dest = "fullscreen", default = None, action = 'store_true',
		help = "Use fullscreen display."
	)
	parser.add_argument('-w', '--windowed',
		dest = "windowed", default = None, action = 'store_true',
		help = "Use windowed display."
	)
	parser.add_argument('-s', '--seed',
		dest = "rng_seed", type = int, default = None,
		help = "Seed for randomness when starting a new game."
	)
	parser.add_argument('-n', '--new-game',
		dest = "start_new_game", action = 'store_true', default = False,
		help = "Start a new game without going through the menu."
	)
	args = parser.parse_args()

	config = normalize_config(load_config())
	keybindings = load_keys()

	if args.resolution is not None:
		resolution = args.resolution
	else:
		resolution = config['display']['width'], config['display']['height']
	if args.windowed is not None:
		fullscreen = False
	elif args.fullscreen is not None:
		fullscreen = True
	else:
		fullscreen = config['display']['fullscreen']

	main_view_opts = {
		'dialog_max_width': config['ui']['dialog_max_width']
	}
	if 'status_bar_width' in config['ui']:
		main_view_opts['bar_width'] = config['ui']['status_bar_width']

	if config['debug']['log_events']:
		data.event_debug = True
	main_view_opts['ignore_fov'] = config['debug']['ignore_fov']

	with ui.Display(screen_dim=resolution, fullscreen=fullscreen, title="Wastrl", font_opts=config['tdl_font']) as disp:
		def start_game(seed=None, do_intro=True):
			loading_view = basic_ui.LoadingView("Creating game", "Please wait while the game is being created.", max_width=config['ui']['dialog_max_width'])
			disp.views.add(loading_view)
			if seed is None:
				seed = int(time.time() * 1000)
			the_game = game.Game(seed, starter_kit=config['debug']['starter_kit'])
			view = main_view.MainView(disp, keybindings, the_game, keybindings=keybindings['main'], **main_view_opts)
			loading_view.close()
			disp.views.add(view)
			if do_intro:
				text = texts.make_helpful_intro(keybindings['main'], commands.help)
				intro_view = basic_ui.ViewWithKeys("Wastrl", text, basic_ui.TextWindow, keybindings=keybindings['dialogs'], max_width=config['ui']['dialog_max_width'])
				disp.views.add(intro_view)
		if args.start_new_game:
			start_game(seed=args.rng_seed, do_intro=False)
		else:
			disp.views.add(menu.Menu(disp, keybindings, start_game, keybindings=keybindings['dialogs'], dialog_max_width=config['ui']['dialog_max_width']))
