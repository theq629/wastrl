import os
import sys
import appdirs
from .. import ui
from ..ui import basic as basic_ui
from ..ui import keys
from .. import game
from . import main_view
from . import commands
from . import intro

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
	keybindings = keys.load(path)
	try:
		keys.verify(keybindings, sections=sections, commands=dir(commands))
	except keys.UnknownSection as e:
		print(f"warning: unknown section in keys file: {e}", file=sys.stderr)
	except keys.UnknownKey as e:
		print(f"warning: unknown key in keys file: {e}", file=sys.stderr)
	except keys.UnknownCommand as e:
		print(f"warning: unknown command in keys file: {e}", file=sys.stderr)
	for section in sections:
		if section not in keybindings:
			keybindings[section] = {}
	return keybindings

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
	parser.add_argument('-s', '--seed',
		dest = "rng_seed", type = int, default = 0,
		help = "Seed for randomness."
	)
	parser.add_argument('-I', '--skip-intro',
		dest = "do_intro", default = True, action = 'store_false',
		help = "Skip the intro message."
	)
	args = parser.parse_args()

	keybindings = load_keys()

	the_game = game.Game(args.rng_seed)

	with ui.Display(screen_dim=args.resolution, fullscreen=args.fullscreen, title="Wastrl") as disp:
		disp.views.add(main_view.MainView(disp, the_game, keybindings=keybindings['main']))
		if args.do_intro:
			disp.views.add(basic_ui.TextView("Wastrl", intro.intro, keybindings=keybindings['dialogs']))
