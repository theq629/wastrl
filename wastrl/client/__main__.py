import os
import sys
import appdirs
import configparser
from .. import ui
from ..ui import basic as basic_ui
from ..ui import keys
from .. import game
from . import main_view
from . import end_view
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

	with ui.Display(screen_dim=args.resolution, fullscreen=args.fullscreen, title="Wastrl", font_path=args.font_path) as disp:
		disp.views.add(end_view.EndView(disp, the_game, keybindings=keybindings['dialogs']))
		disp.views.add(main_view.MainView(disp, keybindings, the_game, keybindings=keybindings['main']))
		if args.do_intro:
			disp.views.add(basic_ui.ViewWithKeys("Wastrl", texts.intro, basic_ui.TextWindow, keybindings=keybindings['dialogs'], max_width=80))
