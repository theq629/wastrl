import os
import sys
import time
import appdirs
import configparser
from .. import ui
from ..ui import basic as basic_ui
from ..ui import keys
from .. import game
from . import main_view
from . import menu
from . import commands
from . import texts

prog_name = "wastrl"
prog_author = "theq629"

def int_pair(s):
	x, y = s.split(',')
	return (int(x), int(y))

def load_keys():
	sections = { "main", "dialogs" }
	path = os.path.join(appdirs.user_data_dir(prog_name, prog_author), "keys")
	if not os.path.exists(path):
		print(f"warning: keys config file does not exist: {path}", file=sys.stderr)
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

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Wastrl")
	parser.add_argument('-r', '--resolution', metavar="X,Y",
		dest = "resolution", type = int_pair, default = (80, 50),
		help = "Resolution of display in characters."
	)
	parser.add_argument('-F', '--font', metavar="PATH",
		dest = "font_path", type = str, default = None,
		help = "Path to font image file."
	)
	parser.add_argument('-f', '--fullscreen',
		dest = "fullscreen", default = False, action = 'store_true',
		help = "Use fullscreen display."
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

	keybindings = load_keys()

	with ui.Display(screen_dim=args.resolution, fullscreen=args.fullscreen, title="Wastrl", font_path=args.font_path) as disp:
		def start_game(seed=None, do_intro=True):
			loading_view = basic_ui.LoadingView("Creating game", "Please wait while the game is being created.")
			disp.views.add(loading_view)
			if seed is None:
				seed = int(time.time() * 1000)
			the_game = game.Game(seed)
			view = main_view.MainView(disp, keybindings, the_game, keybindings=keybindings['main'])
			loading_view.close()
			disp.views.add(view)
			if do_intro:
				text = texts.make_helpful_intro(keybindings['main'], commands.help)
				intro_view = basic_ui.ViewWithKeys("Wastrl", text, basic_ui.TextWindow, keybindings=keybindings['dialogs'], max_width=80)
				disp.views.add(intro_view)
		if args.start_new_game:
			start_game(seed=args.rng_seed, do_intro=False)
		else:
			disp.views.add(menu.Menu(disp, keybindings, start_game, keybindings=keybindings['dialogs']))
